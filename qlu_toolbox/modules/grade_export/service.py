from __future__ import annotations

import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Callable

from qlu_toolbox.core.browser_component import (
    DOWNLOAD_SIZE_MIB,
    INSTALLED_SIZE_MIB,
    configure_browser_environment,
)
from qlu_toolbox.core.paths import AppPaths

from .domain import (
    BASE_URL,
    CancelledError,
    ExportError,
    ExportOptions,
    atomic_save,
    build_score_url,
    extract_base_prefix,
    is_logged_in_url,
    output_path,
)


LOGIN_TIMEOUT_SECONDS = 15 * 60
EventSink = Callable[[dict[str, object]], None]


STAGES = {
    "environment": "检查运行环境",
    "browser": "启动浏览器",
    "login": "等待用户登录",
    "query": "查询成绩",
    "validate": "生成并校验文件",
    "save": "保存结果",
}


def _event(emit: EventSink, kind: str, **payload: object) -> None:
    emit({"type": kind, **payload})


def _check_cancelled(cancel_event: threading.Event) -> None:
    if cancel_event.is_set():
        raise CancelledError("操作已取消")


def _browser_candidates(preference: str) -> tuple[tuple[str | None, str], ...]:
    candidates = {
        "edge": ("msedge", "Microsoft Edge"),
        "chrome": ("chrome", "Google Chrome"),
        "chromium": (None, "备用 Chromium"),
    }
    order = ["edge", "chrome", "chromium"]
    if preference in candidates:
        order.remove(preference)
        order.insert(0, preference)
    return tuple(candidates[item] for item in order)


def _launch_context(
    playwright,
    playwright_error,
    options: ExportOptions,
    emit: EventSink,
    cancel_event: threading.Event,
    browser_ready_event: threading.Event,
):
    paths = AppPaths.discover()
    paths.ensure()
    transient_root: Path | None = None
    if options.keep_login_state:
        profile_root = paths.profile_dir / "grade-export"
        profile_root.mkdir(parents=True, exist_ok=True)
    else:
        transient_root = Path(tempfile.mkdtemp(prefix="grade-export-", dir=paths.data_dir))
        profile_root = transient_root

    managed_browser_installed = Path(playwright.chromium.executable_path).is_file()
    failures: list[str] = []
    for channel, label in _browser_candidates(options.preferred_browser):
        profile_dir = profile_root / f"browser-{channel or 'chromium'}"
        try:
            kwargs: dict[str, object] = {
                "user_data_dir": str(profile_dir),
                "headless": False,
                "accept_downloads": True,
                "no_viewport": True,
            }
            if channel:
                kwargs["channel"] = channel
            context = playwright.chromium.launch_persistent_context(**kwargs)
            _event(emit, "log", message=f"已启动 {label}")
            return context, transient_root
        except playwright_error as exc:
            failures.append(f"{label}: {str(exc).splitlines()[0]}")
            _event(emit, "log", message=f"{label} 不可用，正在尝试其他浏览器")

    if not managed_browser_installed:
        _event(
            emit,
            "browser_required",
            stage="browser",
            message="未找到可用的 Edge 或 Chrome，需要下载备用浏览器组件。",
            downloadSizeMiB=DOWNLOAD_SIZE_MIB,
            installedSizeMiB=INSTALLED_SIZE_MIB,
        )
        while not browser_ready_event.wait(0.25):
            _check_cancelled(cancel_event)
        browser_ready_event.clear()
        _check_cancelled(cancel_event)
        _event(emit, "status", stage="browser", message="浏览器组件已就绪，正在继续任务…")
        profile_dir = profile_root / "browser-chromium"
        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                headless=False,
                accept_downloads=True,
                no_viewport=True,
            )
            _event(emit, "log", message="已启动备用 Chromium")
            return context, transient_root
        except playwright_error as exc:
            failures.append(f"备用 Chromium: {str(exc).splitlines()[0]}")

    if transient_root:
        shutil.rmtree(transient_root, ignore_errors=True)
    detail = "；".join(failures)
    raise ExportError(f"没有可用浏览器。请安装或启用 Edge、Chrome，或下载备用 Chromium。{detail}")


def _wait_for_login(
    context,
    emit: EventSink,
    cancel_event: threading.Event,
    manual_continue_event: threading.Event,
):
    deadline = time.monotonic() + LOGIN_TIMEOUT_SECONDS
    seen_urls: set[str] = set()
    while time.monotonic() < deadline:
        _check_cancelled(cancel_event)
        pages = list(context.pages)
        detected_page = None
        for candidate in pages:
            try:
                page_state = candidate.evaluate(
                    """
                    () => ({
                        url: window.location.href,
                        loggedInDom: Boolean(
                            document.querySelector('#sessionUser')
                            || document.querySelector('#sessionUserKey')
                            || document.querySelector('a[href*="logout"]')
                        ),
                    })
                    """
                )
                url = page_state.get("url", "")
                logged_in_dom = bool(page_state.get("loggedInDom"))
            except Exception:
                url = candidate.url or ""
                logged_in_dom = False
            if url and url not in seen_urls and url != "about:blank":
                seen_urls.add(url)
                _event(emit, "log", message=f"浏览器页面：{url}")
            if is_logged_in_url(url) or (
                logged_in_dom and (
                    url.startswith("https://webvpn.sdnu.edu.cn/")
                    or url.startswith("https://jwxt.sdnu.edu.cn/jwglxt/")
                )
            ):
                detected_page = candidate
                break

        if detected_page:
            _event(emit, "log", message="已自动识别登录成功")
            return detected_page

        if manual_continue_event.is_set():
            manual_continue_event.clear()
            page = None
            for candidate in reversed(pages):
                try:
                    current_url = candidate.evaluate("() => window.location.href")
                except Exception:
                    current_url = candidate.url or ""
                if is_logged_in_url(current_url):
                    page = candidate
                    break
            if page:
                _event(emit, "log", message="已验证当前页面登录状态")
                return page
            _event(
                emit,
                "status",
                stage="login",
                message="尚未检测到登录成功，请在工具箱打开的浏览器中完成登录。",
            )
        time.sleep(0.5)
    raise ExportError("等待登录超时，请重新开始任务")


def _friendly_error(exc: Exception) -> tuple[str, str]:
    text = str(exc).strip()
    if "net::ERR" in text:
        return "NETWORK_UNAVAILABLE", "无法访问学校教务系统，请检查网络、校园 VPN 或服务器状态。"
    if "Target page, context or browser has been closed" in text:
        return "BROWSER_CLOSED", "浏览器已被关闭，导出未完成。"
    if "Executable doesn't exist" in text:
        return "BROWSER_MISSING", "没有找到兼容浏览器，请安装 Edge、Chrome 或运行浏览器组件安装。"
    if isinstance(exc, PermissionError):
        return "OUTPUT_NOT_WRITABLE", "保存目录不可写，请选择其他文件夹。"
    if isinstance(exc, (FileExistsError, NotADirectoryError)):
        return "OUTPUT_INVALID", "所选保存位置不是有效文件夹，请重新选择。"
    if isinstance(exc, OSError):
        return "OUTPUT_ERROR", "无法使用所选保存位置，请检查磁盘空间或更换文件夹。"
    return "EXPORT_FAILED", text or exc.__class__.__name__


def run_export(
    options: ExportOptions,
    emit: EventSink,
    cancel_event: threading.Event,
    manual_continue_event: threading.Event,
    browser_ready_event: threading.Event,
) -> int:
    context = None
    transient_root: Path | None = None
    try:
        _event(emit, "status", stage="environment", message="正在检查运行环境…")
        options.output_dir.mkdir(parents=True, exist_ok=True)
        probe = options.output_dir / ".sdnu-toolbox-write-test"
        probe.write_bytes(b"")
        probe.unlink()
        _check_cancelled(cancel_event)

        configure_browser_environment(AppPaths.discover())
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise ExportError("缺少 Playwright 运行组件，请重新安装 SDNU 工具箱。") from exc

        _event(emit, "status", stage="browser", message="正在启动浏览器…")
        with sync_playwright() as playwright:
            context, transient_root = _launch_context(
                playwright,
                PlaywrightError,
                options,
                emit,
                cancel_event,
                browser_ready_event,
            )
            page = context.pages[0] if context.pages else context.new_page()
            try:
                page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
            except PlaywrightTimeoutError:
                _event(emit, "log", message="VPN 门户加载较慢，请继续在浏览器中操作")

            _event(
                emit,
                "status",
                stage="login",
                message="请在浏览器中依次完成：1) WebVPN SSO 一号通登录 → 2) VPN 内点击「本科教务」→ 3) 教务页面使用账号密码登录（勿点 SSO）",
            )
            _event(emit, "log", message="注意：教务登录页请使用账号+密码+验证码登录，不要点击 SSO 登录按钮（会导致循环跳转）")
            login_page = _wait_for_login(
                context, emit, cancel_event, manual_continue_event
            )
            _check_cancelled(cancel_event)

            base_prefix = extract_base_prefix(login_page.url)
            _event(emit, "log", message=f"检测到教务系统前缀：{base_prefix}")
            score_url = build_score_url(base_prefix)
            _event(emit, "status", stage="query", message="正在打开学生成绩查询…")
            login_page.goto(score_url, wait_until="domcontentloaded", timeout=60_000)
            login_page.wait_for_selector("#xnm", state="attached", timeout=30_000)
            login_page.wait_for_selector("#xqm", state="attached", timeout=30_000)
            login_page.wait_for_function(
                """
                () => {
                    const year = document.getElementById('xnm');
                    const semester = document.getElementById('xqm');
                    return year && semester
                        && year.options.length > 1 && semester.options.length > 1;
                }
                """,
                timeout=30_000,
            )

            # 先获取下拉框选项用于诊断
            semester_options_diag = login_page.evaluate(
                """
                () => {
                    const yearSelect = document.getElementById('xnm');
                    const semesterSelect = document.getElementById('xqm');
                    return {
                        yearOptions: yearSelect ? Array.from(yearSelect.options).map(o => ({v: o.value, t: (o.textContent||'').trim()})) : [],
                        semesterOptions: semesterSelect ? Array.from(semesterSelect.options).map(o => ({v: o.value, t: (o.textContent||'').trim()})) : [],
                    };
                }
                """
            )
            _event(emit, "log", message=f"学年选项：{semester_options_diag['yearOptions']}")
            _event(emit, "log", message=f"学期选项：{semester_options_diag['semesterOptions']}")

            selection = login_page.evaluate(
                """
                ({academicYear, semester}) => {
                    const yearSelect = document.getElementById('xnm');
                    const semesterSelect = document.getElementById('xqm');
                    if (!yearSelect || !semesterSelect) {
                        return {ok: false, message: '成绩页面缺少学年或学期控件'};
                    }
                    const schoolYear = `${academicYear}-${Number(academicYear) + 1}`;
                    const yearOption = Array.from(yearSelect.options).find(option =>
                        option.value === academicYear
                        || (option.textContent || '').includes(schoolYear)
                    );
                    const semesterTexts = {'3': ['1', '第一', '一'], '12': ['2', '第二', '二']};
                    const semesterOption = Array.from(semesterSelect.options).find(option => {
                        if (option.value === semester) return true;
                        const text = (option.textContent || '').trim();
                        return (semesterTexts[semester] || []).some(name => text.includes(name));
                    });
                    if (!yearOption) return {ok: false, message: `成绩页面中没有 ${schoolYear} 学年`};
                    if (!semesterOption) return {ok: false, message: '成绩页面中没有所选学期'};

                    // 使用 jQuery val() 设置 select 值
                    const $ = window.jQuery || window.$;
                    if ($) {
                        $('#xnm').val(yearOption.value);
                        $('#xqm').val(semesterOption.value);
                        // 触发 chosen 更新
                        $('#xnm').trigger('chosen:updated');
                        $('#xqm').trigger('chosen:updated');
                        // 直接点击 chosen 下拉菜单中对应的选项（最可靠的方式）
                        const semesterIndex = Array.from(semesterSelect.options).indexOf(semesterOption);
                        const yearIndex = Array.from(yearSelect.options).indexOf(yearOption);
                        // 打开并点击 chosen 选项
                        const semesterChosen = $('#xqm_chosen');
                        const yearChosen = $('#xnm_chosen');
                        if (semesterChosen.length && semesterIndex > 0) {
                            semesterChosen.find('.chosen-single').trigger('mousedown');
                            semesterChosen.find(`.chosen-results li[data-option-array-index="${semesterIndex}"]`).trigger('mouseup');
                        }
                        if (yearChosen.length && yearIndex > 0) {
                            yearChosen.find('.chosen-single').trigger('mousedown');
                            yearChosen.find(`.chosen-results li[data-option-array-index="${yearIndex}"]`).trigger('mouseup');
                        }
                        // 确保 change 事件触发
                        $('#xnm').change();
                        $('#xqm').change();
                    } else {
                        yearSelect.value = yearOption.value;
                        semesterSelect.value = semesterOption.value;
                        yearSelect.dispatchEvent(new Event('change', {bubbles: true}));
                        semesterSelect.dispatchEvent(new Event('change', {bubbles: true}));
                    }
                    return {
                        ok: true,
                        academicYearValue: yearOption.value,
                        semesterValue: semesterOption.value,
                    };
                }
                """,
                {"academicYear": options.academic_year, "semester": options.semester_value},
            )
            if not selection.get("ok"):
                raise ExportError(selection.get("message", "无法设置学年和学期"))
            export_year = selection["academicYearValue"]
            export_semester = selection["semesterValue"]
            _event(emit, "log", message=f"已设置学年={export_year} 学期={export_semester}")

            _event(emit, "log", message="正在点击查询按钮…")
            query_started = login_page.evaluate(
                """
                () => {
                    const button = document.getElementById('search_go');
                    if (!button) return false;
                    button.click();
                    return true;
                }
                """
            )
            if not query_started:
                raise ExportError("成绩页面缺少查询按钮，教务系统页面可能已更新")
            _event(emit, "log", message="查询按钮已点击，等待成绩数据加载…")
            login_page.wait_for_timeout(800)
            try:
                login_page.wait_for_function(
                    "() => !window.jQuery || window.jQuery.active === 0", timeout=15_000
                )
                _event(emit, "log", message="成绩数据加载完成")
            except PlaywrightTimeoutError:
                _event(emit, "log", message="成绩查询响应较慢，将继续尝试导出")
            _check_cancelled(cancel_event)

            _event(emit, "status", stage="validate", message="正在从页面抓取成绩数据并生成文件…")
            from io import BytesIO
            from xml.sax.saxutils import escape as xml_escape
            from zipfile import ZIP_DEFLATED, ZipFile

            scraped = login_page.evaluate(
                """
                () => {
                    const tables = document.querySelectorAll('table');
                    let targetTable = null;
                    for (const t of tables) {
                        if (t.rows.length > 1) {
                            const hds = [];
                            for (const c of t.rows[0].cells) hds.push((c.textContent || '').trim());
                            const hs = hds.join(' ');
                            if (hs.includes('课程') || hs.includes('成绩') || hs.includes('学分')) {
                                targetTable = t; break;
                            }
                        }
                    }
                    if (!targetTable) {
                        for (const t of tables) {
                            if (t.rows.length >= 2) { targetTable = t; break; }
                        }
                    }
                    if (!targetTable) return {ok: false, message: '未找到成绩数据表格'};
                    const headers = [];
                    for (const c of targetTable.rows[0].cells) headers.push((c.textContent || '').trim());
                    const rows = [];
                    for (let i = 1; i < targetTable.rows.length; i++) {
                        const row = [];
                        for (const c of targetTable.rows[i].cells) row.push((c.textContent || '').trim());
                        if (row.some(v => v)) rows.push(row);
                    }
                    return {ok: true, headers, rows, rowCount: rows.length};
                }
                """
            )
            if not scraped.get("ok"):
                raise ExportError(scraped.get("message", "无法从页面抓取成绩数据"))

            raw_rows = scraped["rows"]
            _event(emit, "log", message=f"抓取到 {len(raw_rows)} 条成绩记录")

            # SDNU 正方教务系统成绩表格的列映射（每列位置固定，表头为空）
            # 索引: 1=学年 2=学期 3=课程代码 4=课程名称 6=学分 11=开课学院 15=教学班 22=成绩
            COL_MAP = {
                "学年": 1,
                "学期": 2,
                "课程代码": 3,
                "课程名称": 4,
                "学分": 6,
                "开课学院": 11,
                "教学班": 15,
                "成绩": 22,
            }
            # GPA 计算器需要的列
            OUTPUT_HEADERS = ["课程名称", "学分", "成绩", "成绩分项", "学年", "学期", "课程代码", "开课学院", "教学班"]

            def _safe_get(row: list[str], idx: int) -> str:
                return row[idx] if idx < len(row) else ""

            rows: list[list[str]] = []
            for raw in raw_rows:
                # SDNU 没有分项成绩，统一填 "总评"
                mapped = [
                    _safe_get(raw, COL_MAP["课程名称"]),
                    _safe_get(raw, COL_MAP["学分"]),
                    _safe_get(raw, COL_MAP["成绩"]),
                    "总评",
                    _safe_get(raw, COL_MAP["学年"]),
                    _safe_get(raw, COL_MAP["学期"]),
                    _safe_get(raw, COL_MAP["课程代码"]),
                    _safe_get(raw, COL_MAP["开课学院"]),
                    _safe_get(raw, COL_MAP["教学班"]),
                ]
                if mapped[0]:  # 只要有课程名称就保留
                    rows.append(mapped)

            _event(emit, "log", message=f"处理后 {len(rows)} 条记录，列名：{OUTPUT_HEADERS}")

            # 收集所有文本 → shared strings
            all_texts: list[str] = []
            text_index: dict[str, int] = {}
            def _register(value: str) -> int:
                clean = ''.join(c for c in value if ord(c) >= 32 or c in '\t\n\r')
                if clean not in text_index:
                    text_index[clean] = len(all_texts)
                    all_texts.append(clean)
                return text_index[clean]

            table_data: list[list[int]] = []
            table_data.append([_register(h) for h in OUTPUT_HEADERS])
            for row in rows:
                table_data.append([_register(c) for c in row])

            # 构建 shared strings XML
            sst_items = []
            for text in all_texts:
                escaped = xml_escape(text)
                sst_items.append(f'<si><t xml:space="preserve">{escaped}</t></si>')
            sst_xml = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<sst count="{len(all_texts)}" uniqueCount="{len(all_texts)}"'
                f' xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'{"".join(sst_items)}'
                f'</sst>'
            )

            # 构建 worksheet XML（参考 QLU 正方导出的格式）
            def _col_name(idx: int) -> str:
                r = ""
                while idx >= 0:
                    r = chr(ord("A") + idx % 26) + r
                    idx = idx // 26 - 1
                return r

            last_col = _col_name(len(OUTPUT_HEADERS) - 1)
            last_row = len(table_data)

            sheet_rows = []
            for ri, rd in enumerate(table_data):
                cells = []
                for ci, si in enumerate(rd):
                    ref = f'{_col_name(ci)}{ri + 1}'
                    cells.append(f'<c r="{ref}" t="s"><v>{si}</v></c>')
                sheet_rows.append(f'<row r="{ri + 1}">{"".join(cells)}</row>')

            sheet_xml = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<dimension ref="A1:{last_col}{last_row}"/>'
                f'<sheetViews><sheetView workbookViewId="0" tabSelected="true"/></sheetViews>'
                f'<sheetFormatPr defaultRowHeight="15.0"/>'
                f'<cols>'
                + ''.join(f'<col min="{i+1}" max="{i+1}" width="14.0" customWidth="true"/>' for i in range(len(OUTPUT_HEADERS)))
                + f'</cols>'
                f'<sheetData>{"".join(sheet_rows)}</sheetData>'
                f'</worksheet>'
            )

            # workbook.xml（匹配 QLU 格式）
            wb_xml = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
                f' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<workbookPr date1904="false"/>'
                f'<bookViews><workbookView activeTab="0"/></bookViews>'
                f'<sheets><sheet name="sheet1" r:id="rId3" sheetId="1"/></sheets>'
                f'</workbook>'
            )

            # styles.xml（参考 QLU 格式）
            styles_xml = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                f'<numFmts count="0"/>'
                f'<fonts count="1"><font><sz val="11.0"/><name val="Calibri"/><family val="2"/><scheme val="minor"/></font></fonts>'
                f'<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
                f'<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
                f'<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                f'<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
                f'</styleSheet>'
            )

            # 关系文件 - 这是 Excel 能打开的关键！
            # _rels/.rels 必须包含 docProps 的引用
            root_rels = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
                f'<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                f'</Relationships>'
            )
            # xl/_rels/workbook.xml.rels 必须包含 sharedStrings 和 styles
            wb_rels = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>'
                f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                f'<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                f'</Relationships>'
            )
            # docProps
            app_xml = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
                f'<Application>SDNU Toolbox</Application></Properties>'
            )
            core_xml = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
                f' xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"'
                f' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                f'<dcterms:created xsi:type="dcterms:W3CDTF">2026-07-17T00:00:00Z</dcterms:created>'
                f'<dc:creator>SDNU Toolbox</dc:creator></cp:coreProperties>'
            )

            content_types = (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                f'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                f'<Default Extension="xml" ContentType="application/xml"/>'
                f'<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
                f'<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                f'<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
                f'<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                f'<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                f'</Types>'
            )

            # 打包为 xlsx
            buf = BytesIO()
            with ZipFile(buf, "w", ZIP_DEFLATED) as zf:
                for fname, fdata in [
                    ("[Content_Types].xml", content_types),
                    ("_rels/.rels", root_rels),
                    ("xl/workbook.xml", wb_xml),
                    ("xl/_rels/workbook.xml.rels", wb_rels),
                    ("xl/worksheets/sheet1.xml", sheet_xml),
                    ("xl/sharedStrings.xml", sst_xml),
                    ("xl/styles.xml", styles_xml),
                    ("docProps/app.xml", app_xml),
                    ("docProps/core.xml", core_xml),
                ]:
                    zf.writestr(fname, fdata.encode("utf-8"))
            content = buf.getvalue()

            _event(emit, "status", stage="save", message="正在保存 Excel 文件…")
            destination = output_path(options, ".xlsx")
            atomic_save(destination, content)
            _event(emit, "success", path=str(destination))
            return 0
    except CancelledError:
        _event(emit, "cancelled", message="操作已取消")
        return 2
    except Exception as exc:
        code, message = _friendly_error(exc)
        _event(emit, "error", code=code, message=message)
        return 1
    finally:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass
        if transient_root is not None:
            shutil.rmtree(transient_root, ignore_errors=True)
