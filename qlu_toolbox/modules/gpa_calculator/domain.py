from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
import re
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
REQUIRED_HEADERS = ("课程名称", "学分", "成绩", "成绩分项")
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_XML_SIZE = 50 * 1024 * 1024

LETTER_GRADE_POINTS = {
    "A+": Decimal("5.0"), "A": Decimal("4.5"), "A-": Decimal("4.2"),
    "B+": Decimal("3.8"), "B": Decimal("3.5"), "B-": Decimal("3.2"),
    "C+": Decimal("2.8"), "C": Decimal("2.5"), "C-": Decimal("2.2"),
    "D": Decimal("1.5"), "F": Decimal("0"),
}
CHINESE_GRADE_POINTS = {
    "优秀": Decimal("4.5"), "良好": Decimal("3.5"), "中等": Decimal("2.5"),
    "及格": Decimal("1.5"), "不及格": Decimal("0"),
}


class GPAParseError(ValueError):
    pass


@dataclass(frozen=True)
class ScoreRow:
    name: str
    score: str
    is_final: bool


@dataclass(frozen=True)
class ParsedCourse:
    id: str
    name: str
    code: str
    college: str
    teaching_class: str
    academic_year: str
    semester: str
    credit: float | None
    components: list[ScoreRow]
    final_score: str
    grade_point: float | None
    included: bool
    issue: str


def _normalized(value: str) -> str:
    return re.sub(r"\s+", "", value).strip("\ufeff")


def _column_index(reference: str) -> int:
    letters = "".join(char for char in reference.upper() if char.isalpha())
    if not letters:
        return 0
    result = 0
    for char in letters:
        result = result * 26 + ord(char) - ord("A") + 1
    return result - 1


def _safe_archive_read(archive: ZipFile, name: str) -> bytes:
    try:
        info = archive.getinfo(name)
    except KeyError as exc:
        raise GPAParseError("Excel 文件结构不完整") from exc
    if info.file_size > MAX_XML_SIZE:
        raise GPAParseError("Excel 工作表过大，无法安全读取")
    return archive.read(info)


def _first_sheet_path(archive: ZipFile) -> str:
    workbook = ElementTree.fromstring(_safe_archive_read(archive, "xl/workbook.xml"))
    sheet = workbook.find(f".//{{{MAIN_NS}}}sheets/{{{MAIN_NS}}}sheet")
    if sheet is None:
        raise GPAParseError("Excel 中没有可读取的工作表")
    relation_id = sheet.get(f"{{{REL_NS}}}id", "")
    relationships = ElementTree.fromstring(
        _safe_archive_read(archive, "xl/_rels/workbook.xml.rels")
    )
    target = ""
    for relationship in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship"):
        if relationship.get("Id") == relation_id:
            target = relationship.get("Target", "")
            break
    if not target:
        raise GPAParseError("无法定位 Excel 工作表")
    if target.startswith("/"):
        path = PurePosixPath(target.lstrip("/"))
    else:
        path = PurePosixPath("xl") / target
    parts: list[str] = []
    for part in path.parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part not in {"", "."}:
            parts.append(part)
    resolved = "/".join(parts)
    if not resolved.startswith("xl/"):
        raise GPAParseError("Excel 工作表路径无效")
    return resolved


def _read_rows(path: Path) -> list[list[str]]:
    if not path.is_file():
        raise GPAParseError("所选文件不存在")
    if path.suffix.lower() != ".xlsx":
        raise GPAParseError("请选择分项成绩导出的 .xlsx 文件")
    if path.stat().st_size > MAX_FILE_SIZE:
        raise GPAParseError("Excel 文件超过 20 MB，无法读取")
    try:
        with ZipFile(path) as archive:
            shared_strings: list[str] = []
            if "xl/sharedStrings.xml" in archive.namelist():
                shared_root = ElementTree.fromstring(
                    _safe_archive_read(archive, "xl/sharedStrings.xml")
                )
                for item in shared_root.findall(f"{{{MAIN_NS}}}si"):
                    shared_strings.append(
                        "".join(node.text or "" for node in item.findall(f".//{{{MAIN_NS}}}t"))
                    )

            sheet_root = ElementTree.fromstring(
                _safe_archive_read(archive, _first_sheet_path(archive))
            )
            result: list[list[str]] = []
            for row in sheet_root.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row"):
                values: dict[int, str] = {}
                for cell in row.findall(f"{{{MAIN_NS}}}c"):
                    index = _column_index(cell.get("r", ""))
                    cell_type = cell.get("t", "")
                    if cell_type == "inlineStr":
                        value = "".join(
                            node.text or "" for node in cell.findall(f".//{{{MAIN_NS}}}t")
                        )
                    else:
                        node = cell.find(f"{{{MAIN_NS}}}v")
                        value = node.text if node is not None and node.text is not None else ""
                        if cell_type == "s" and value:
                            try:
                                value = shared_strings[int(value)]
                            except (ValueError, IndexError) as exc:
                                raise GPAParseError("Excel 共享文本索引无效") from exc
                    values[index] = value.strip()
                if values:
                    result.append([values.get(index, "") for index in range(max(values) + 1)])
            return result
    except (BadZipFile, ElementTree.ParseError, OSError) as exc:
        raise GPAParseError("无法读取该 XLSX 文件，请重新导出后再试") from exc


def _decimal(value: str) -> Decimal | None:
    try:
        result = Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        return None
    return result if result.is_finite() else None


def grade_point(score: str) -> Decimal | None:
    normalized = _normalized(score).upper()
    if normalized in LETTER_GRADE_POINTS:
        return LETTER_GRADE_POINTS[normalized]
    if normalized in CHINESE_GRADE_POINTS:
        return CHINESE_GRADE_POINTS[normalized]
    numeric = _decimal(score)
    if numeric is None or numeric < 0 or numeric > 100:
        return None
    # SDNU 绩点公式: (分数 - 50) / 10
    # 例如: 100→5.0, 92→4.2, 85→3.5, 70→2.0, 60→1.0
    if numeric >= 60:
        point = (numeric - Decimal("50")) / Decimal("10")
        return min(point, Decimal("5.0"))
    return Decimal("0")


def parse_grade_xlsx(file_path: str | Path) -> dict[str, object]:
    path = Path(file_path).expanduser()
    rows = _read_rows(path)
    if not rows:
        raise GPAParseError("Excel 中没有成绩数据")

    header_row_index = -1
    headers: list[str] = []
    for index, row in enumerate(rows[:10]):
        normalized = {_normalized(value) for value in row}
        if all(required in normalized for required in REQUIRED_HEADERS):
            header_row_index = index
            headers = [_normalized(value) for value in row]
            break
    if header_row_index < 0:
        raise GPAParseError("文件缺少课程名称、学分、成绩或成绩分项列")

    columns = {name: index for index, name in enumerate(headers) if name}
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in rows[header_row_index + 1:]:
        record = {
            name: row[index].strip() if index < len(row) else ""
            for name, index in columns.items()
        }
        if not any(record.values()) or not record.get("课程名称", ""):
            continue
        key = (
            record.get("学年", ""), record.get("学期", ""),
            record.get("课程代码", ""), record.get("教学班", ""),
            record.get("课程名称", ""),
        )
        grouped.setdefault(key, []).append(record)

    courses: list[ParsedCourse] = []
    warnings: list[str] = []
    for number, records in enumerate(grouped.values(), start=1):
        first = records[0]
        components = [
            ScoreRow(
                name=record.get("成绩分项", "") or "未命名分项",
                score=record.get("成绩", ""),
                is_final=_normalized(record.get("成绩分项", "")) in {"总评", "总评成绩"},
            )
            for record in records
        ]
        finals = [component for component in components if component.is_final]
        final_score = finals[-1].score if finals else ""
        credit_value = _decimal(first.get("学分", ""))
        point = grade_point(final_score) if final_score else None
        issue = ""
        if not finals:
            issue = "没有找到总评成绩"
        elif len({item.score for item in finals}) > 1:
            issue = "存在多个不同的总评成绩"
            point = None
        elif credit_value is None or credit_value <= 0:
            issue = "学分无法识别"
        elif point is None:
            issue = "总评成绩无法识别"
        if issue:
            warnings.append(f"{first.get('课程名称', '未命名课程')}：{issue}")
        courses.append(ParsedCourse(
            id=f"course-{number}",
            name=first.get("课程名称", "未命名课程"),
            code=first.get("课程代码", ""),
            college=first.get("开课学院", ""),
            teaching_class=first.get("教学班", ""),
            academic_year=first.get("学年", ""),
            semester=first.get("学期", ""),
            credit=float(credit_value) if credit_value is not None else None,
            components=components,
            final_score=final_score,
            grade_point=float(point) if point is not None else None,
            included=not issue,
            issue=issue,
        ))

    if not courses:
        raise GPAParseError("Excel 中没有可识别的课程")
    return {
        "fileName": path.name,
        "filePath": str(path.resolve()),
        "rowCount": sum(len(records) for records in grouped.values()),
        "courses": [asdict(course) for course in courses],
        "warnings": warnings,
    }
