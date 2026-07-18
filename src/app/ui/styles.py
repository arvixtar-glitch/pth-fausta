"""Generate the centralized application QSS."""

from app.ui import theme


def application_stylesheet() -> str:
    """Return the approved light application stylesheet."""
    return f"""
        QWidget {{ font-family: 'Segoe UI'; font-size: 10pt;
            color: {theme.COLOR_TEXT_PRIMARY}; }}
        QMainWindow, QDialog, #page {{ background: {theme.COLOR_PAGE_BACKGROUND}; }}
        QLabel#h1 {{ font-size: 17pt; font-weight: 600; }}
        QLabel#h2 {{ font-size: 14pt; font-weight: 600; }}
        QLabel#h3 {{ font-size: 12pt; font-weight: 600; }}
        QLabel#secondary {{ color: {theme.COLOR_TEXT_SECONDARY}; }}
        QLabel#error {{ color: {theme.COLOR_ERROR}; }}
        QLabel#success {{ color: {theme.COLOR_SUCCESS}; }}
        QLabel#warning {{ color: {theme.COLOR_WARNING}; }}
        QPushButton {{ padding: 7px 16px; border-radius: {theme.RADIUS_SM}px;
            border: 1px solid {theme.COLOR_BORDER_STRONG}; background: white; }}
        QPushButton:hover {{ border-color: {theme.COLOR_PRIMARY}; }}
        QPushButton:focus, QLineEdit:focus, QComboBox:focus, QTableWidget:focus {{
            border: 2px solid {theme.COLOR_PRIMARY}; }}
        QPushButton#primary {{ background: {theme.COLOR_PRIMARY}; color: white;
            border-color: {theme.COLOR_PRIMARY}; font-weight: 500; }}
        QPushButton#primary:hover {{ background: {theme.COLOR_PRIMARY_HOVER}; }}
        QPushButton#danger {{ background: {theme.COLOR_ERROR}; color: white;
            border-color: {theme.COLOR_ERROR}; }}
        QPushButton:disabled {{ background: #F1F5F9; color: #94A3B8;
            border-color: {theme.COLOR_BORDER}; }}
        QLineEdit, QComboBox {{ padding: 7px; border-radius: {theme.RADIUS_SM}px;
            border: 1px solid {theme.COLOR_BORDER_STRONG}; background: white; }}
        QTabWidget::pane {{ border: 1px solid {theme.COLOR_BORDER}; background: white; }}
        QTabBar::tab {{ padding: 10px 18px; }}
        QTabBar::tab:selected {{ color: {theme.COLOR_PRIMARY};
            border-bottom: 2px solid {theme.COLOR_PRIMARY}; }}
        QHeaderView::section {{ background: #F1F5F9; color: {theme.COLOR_TEXT_SECONDARY};
            padding: 8px; border: none; font-weight: 600; }}
        QTableWidget {{ background: white; border: 1px solid {theme.COLOR_BORDER}; }}
        QTableWidget::item:selected {{ background: {theme.COLOR_ROW_SELECTED};
            color: #0C447C; }}
        QWidget#sidebar {{ background: white; border-right: 1px solid {theme.COLOR_BORDER}; }}
        QPushButton#nav {{ border: none; text-align: left; padding: 10px; }}
        QPushButton#nav:checked {{ background: {theme.COLOR_ROW_SELECTED};
            color: {theme.COLOR_PRIMARY}; font-weight: 600; }}
    """
