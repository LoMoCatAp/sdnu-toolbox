from __future__ import annotations


LIGHT_STYLE = """
* {
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 13px;
    color: #172033;
}
QMainWindow, QWidget#AppRoot, QStackedWidget, QWidget#ContentPage {
    background: #F3F6FA;
}
QWidget#Sidebar {
    background: #FFFFFF;
    border-right: 1px solid #E1E7EF;
}
QLabel#BrandLogo { background: transparent; }
QLabel#BrandName { font-size: 17px; font-weight: 700; color: #101828; }
QLabel#BrandHint, QLabel#Muted, QLabel.muted { color: #68758A; }
QLabel#PageTitle { font-size: 28px; font-weight: 700; color: #101828; }
QLabel#PageSubtitle { color: #657186; font-size: 13px; }
QLabel#SectionHeading { font-size: 17px; font-weight: 700; color: #172033; }
QLabel#SectionCount {
    color: #1769E0;
    background: #EAF2FF;
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 12px;
}
QLabel#FieldHint { color: #7A8799; font-size: 12px; }
QLabel#PathLabel { color: #526176; font-weight: 600; min-width: 64px; }
QLabel#TaskTitle { color: #172033; font-weight: 700; }
QLabel#TaskSummary { color: #526176; font-weight: 600; }
QLabel#TaskStatus { color: #526176; font-weight: 600; }
QLabel#TaskStatus[status="running"] { color: #155FCB; }
QLabel#TaskStatus[status="success"] { color: #087A4F; }
QLabel#TaskStatus[status="failed"] { color: #B42318; }
QPushButton[nav="true"] {
    text-align: left;
    border: 0;
    border-radius: 9px;
    min-height: 22px;
    padding: 11px 15px;
    color: #4A576B;
    background: transparent;
}
QPushButton[nav="true"]:hover { background: #F2F6FB; color: #1769E0; }
QPushButton[nav="true"]:checked {
    background: #EAF2FF;
    color: #155FCB;
    font-weight: 700;
}
QFrame#SidebarFooter {
    background: #F7F9FC;
    border: 1px solid #E7EBF1;
    border-radius: 10px;
}
QFrame#HeroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #EAF3FF, stop:0.68 #F7FAFF, stop:1 #FFF7E2);
    border: 1px solid #D7E5F8;
    border-radius: 16px;
}
QLabel#HeroEyebrow { color: #1769E0; font-size: 12px; font-weight: 700; }
QLabel#HeroTitle { color: #101828; font-size: 27px; font-weight: 700; }
QLabel#HeroSubtitle { color: #526176; font-size: 13px; }
QLabel#Pill {
    color: #35506F;
    background: rgba(255, 255, 255, 190);
    border: 1px solid #D5E2F2;
    border-radius: 11px;
    padding: 4px 10px;
    font-size: 12px;
}
QFrame#Card, QGroupBox#Card, QFrame#ToolCard {
    background: #FFFFFF;
    border: 1px solid #DFE5ED;
    border-radius: 13px;
}
QFrame#ToolCard:hover { border-color: #AFCBF0; background: #FCFDFF; }
QGroupBox#Card {
    margin-top: 12px;
    padding: 18px;
    font-weight: 700;
}
QGroupBox#Card::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 5px;
}
QLabel#ToolIcon {
    background: #EAF2FF;
    color: #1769E0;
    border-radius: 12px;
    font-size: 17px;
    font-weight: 700;
}
QLabel#CategoryBadge {
    color: #6A4C00;
    background: #FFF4D6;
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 12px;
}
QFrame#RecentRow { background: transparent; border-bottom: 1px solid #EDF0F4; }
QFrame#RecentRow:last { border-bottom: 0; }
QFrame#TaskToolbar {
    background: #FFFFFF;
    border: 1px solid #DFE5ED;
    border-radius: 11px;
}
QFrame#TaskCell { background: transparent; }
QLabel#StatusBadge {
    border-radius: 9px;
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 700;
}
QLabel#StatusBadge[status="success"] { color: #087A4F; background: #E8F7F0; }
QLabel#StatusBadge[status="failed"] { color: #B42318; background: #FDECEC; }
QLabel#StatusBadge[status="running"] { color: #155FCB; background: #EAF2FF; }
QLabel#StatusBadge[status="cancelled"], QLabel#StatusBadge[status="interrupted"] {
    color: #5F6B7B; background: #EEF1F5;
}
QLabel#InfoBanner {
    color: #155FCB;
    background: #EDF5FF;
    border: 1px solid #D7E8FF;
    border-radius: 8px;
    padding: 10px 12px;
}
QFrame#SuccessBanner {
    background: #ECF8F1;
    border: 1px solid #CBEBD9;
    border-radius: 9px;
}
QPushButton {
    border: 1px solid #C9D2DE;
    border-radius: 8px;
    background: #FFFFFF;
    min-height: 20px;
    padding: 8px 15px;
}
QPushButton:hover { background: #F5F8FC; border-color: #9FACBD; }
QPushButton:pressed { background: #EAF0F7; }
QPushButton:focus { border-color: #4B91ED; }
QPushButton:disabled { color: #98A3B3; background: #F2F4F7; border-color: #E0E5EC; }
QPushButton[primary="true"] {
    color: white;
    background: #1769E0;
    border-color: #1769E0;
    font-weight: 700;
}
QPushButton[primary="true"]:hover { background: #125BC6; border-color: #125BC6; }
QPushButton[primary="true"]:pressed { background: #0F4FAE; }
QPushButton[danger="true"] { color: #C93838; border-color: #E7B5B5; }
QPushButton[danger="true"]:hover { background: #FFF3F3; border-color: #DA8F8F; }
QPushButton[compact="true"] { min-height: 18px; padding: 6px 12px; }
QPushButton[segment="true"] { min-height: 22px; }
QPushButton[segment="true"]:checked {
    color: #155FCB;
    background: #EAF2FF;
    border-color: #72A7ED;
    font-weight: 700;
}
QPushButton[quiet="true"] { border: 0; background: transparent; color: #1769E0; padding: 5px 2px; }
QPushButton[quiet="true"]:hover { color: #0F4FAE; background: transparent; }
QLineEdit, QComboBox, QPlainTextEdit {
    background: #FFFFFF;
    border: 1px solid #C9D2DE;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #1769E0;
}
QLineEdit, QComboBox { min-height: 20px; }
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus { border: 1px solid #1769E0; }
QLineEdit#DataPath {
    color: #526176;
    background: #F7F9FC;
    border-color: #E3E8EF;
    font-family: "Cascadia Mono", "Consolas", "Microsoft YaHei UI";
    font-size: 12px;
}
QComboBox { padding-right: 30px; }
QComboBox:hover { border-color: #9FACBD; }
QComboBox#SettingsCombo {
    min-height: 24px;
    padding: 9px 38px 9px 12px;
    font-weight: 600;
}
QComboBox#SettingsCombo:hover { background: #FBFCFE; border-color: #78A8E8; }
QComboBox#SettingsCombo:focus { background: #FFFFFF; border-color: #1769E0; }
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    border-left: 1px solid #E5E9F0;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}
QComboBox#SettingsCombo::drop-down { width: 34px; background: #F7F9FC; }
QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #DFE5ED;
    border-radius: 8px;
    padding: 4px;
    selection-background-color: #EAF2FF;
    selection-color: #172033;
    outline: 0;
}
QComboBox QAbstractItemView::item {
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 24px;
}
QComboBox QAbstractItemView::item:hover { background: #F2F6FB; }
QListView#SettingsComboPopup {
    color: #172033;
    background: #FFFFFF;
    border: 1px solid #C9D2DE;
    border-radius: 8px;
    padding: 5px;
    outline: 0;
    font-weight: 400;
}
QListView#SettingsComboPopup::item {
    min-height: 28px;
    padding: 4px 10px;
    border: 0;
    border-radius: 6px;
}
QListView#SettingsComboPopup::item:hover { background: #F2F6FB; }
QListView#SettingsComboPopup::item:selected {
    color: #155FCB;
    background: #EAF2FF;
    font-weight: 600;
}
QPlainTextEdit { font-family: "Cascadia Mono", "Consolas"; font-size: 12px; }
QCheckBox { spacing: 8px; }
QProgressBar {
    border: 0;
    background: #E5EAF1;
    border-radius: 4px;
    min-height: 8px;
    max-height: 8px;
}
QProgressBar::chunk { background: #1769E0; border-radius: 4px; }
QTableWidget {
    background: white;
    alternate-background-color: #FAFBFD;
    border: 1px solid #DFE5ED;
    border-radius: 11px;
    gridline-color: #EDF0F4;
    selection-background-color: #EAF2FF;
    selection-color: #172033;
}
QTableWidget::item { padding: 8px 10px; border-bottom: 1px solid #EEF1F5; }
QTableWidget::item:hover { background: #F4F8FD; }
QHeaderView::section {
    background: #F7F9FC;
    border: 0;
    border-bottom: 1px solid #DFE5ED;
    padding: 10px;
    font-weight: 700;
}
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: 0; }
QSplitter::handle { background: transparent; width: 10px; }
QScrollBar:vertical { width: 10px; background: transparent; }
QScrollBar::handle:vertical { background: #C3CCD8; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #A9B5C4; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QToolTip { background: #172033; color: white; border: 0; padding: 5px; }
"""


DARK_STYLE = LIGHT_STYLE + """
QMainWindow, QWidget#AppRoot, QStackedWidget, QWidget#ContentPage { background: #10141C; }
QWidget#Sidebar { background: #171C25; border-right-color: #2B3442; }
QLabel#PageTitle, QLabel#BrandName, QLabel#SectionHeading, QLabel { color: #E8EDF5; }
QLabel#PageSubtitle, QLabel#BrandHint, QLabel#Muted, QLabel.muted { color: #9AA7B8; }
QLabel#FieldHint, QLabel#PathLabel, QLabel#TaskSummary { color: #9AA7B8; }
QLabel#TaskTitle { color: #E8EDF5; }
QFrame#SidebarFooter { background: #1D2430; border-color: #2B3442; }
QFrame#HeroCard { background: #172338; border-color: #2A466F; }
QLabel#HeroTitle { color: #F2F6FC; }
QLabel#HeroSubtitle { color: #B4C0D0; }
QLabel#Pill { color: #BCD0E9; background: #1E2C40; border-color: #344C6B; }
QFrame#Card, QGroupBox#Card, QFrame#ToolCard { background: #171C25; border-color: #2B3442; }
QFrame#ToolCard:hover { background: #1A202B; border-color: #3D5F8B; }
QFrame#RecentRow { border-bottom-color: #2B3442; }
QFrame#TaskToolbar { background: #171C25; border-color: #2B3442; }
QLabel#InfoBanner { color: #8DBBFA; background: #162A45; border-color: #29496E; }
QFrame#SuccessBanner { background: #153328; border-color: #285441; }
QPushButton { background: #1D2430; border-color: #394456; color: #E8EDF5; }
QPushButton:hover { background: #252E3C; }
QPushButton:pressed { background: #303A49; }
QPushButton[nav="true"] { color: #B4BECC; }
QPushButton[nav="true"]:hover { background: #222A36; }
QPushButton[nav="true"]:checked { background: #19345D; color: #8DBBFA; }
QLineEdit, QComboBox, QPlainTextEdit { background: #111720; border-color: #394456; color: #E8EDF5; }
QLineEdit#DataPath { background: #131923; border-color: #2B3442; color: #AAB6C6; }
QComboBox#SettingsCombo:hover, QComboBox#SettingsCombo:focus { background: #151C27; }
QComboBox::drop-down { border-left-color: #2B3442; }
QComboBox#SettingsCombo::drop-down { background: #1D2430; }
QComboBox QAbstractItemView { background: #171C25; border-color: #2B3442; color: #E8EDF5; }
QComboBox QAbstractItemView::item:hover { background: #222A36; }
QListView#SettingsComboPopup { color: #E8EDF5; background: #171C25; border-color: #394456; }
QListView#SettingsComboPopup::item:hover { background: #222A36; }
QListView#SettingsComboPopup::item:selected { color: #8DBBFA; background: #19345D; }
QTableWidget { background: #171C25; alternate-background-color: #1A202A; border-color: #2B3442; color: #E8EDF5; }
QTableWidget::item { border-bottom-color: #252D39; }
QTableWidget::item:hover { background: #202A38; }
QHeaderView::section { background: #1D2430; border-bottom-color: #2B3442; color: #E8EDF5; }
"""


def stylesheet(theme: str) -> str:
    return DARK_STYLE if theme == "dark" else LIGHT_STYLE
