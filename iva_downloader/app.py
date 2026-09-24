import sys

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from .ui import APP_NAME, MainWindow


def apply_light_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    colors = {
        QPalette.ColorRole.Window: "#f4f6f8",
        QPalette.ColorRole.WindowText: "#1f2937",
        QPalette.ColorRole.Base: "#ffffff",
        QPalette.ColorRole.AlternateBase: "#f8fafc",
        QPalette.ColorRole.ToolTipBase: "#ffffff",
        QPalette.ColorRole.ToolTipText: "#1f2937",
        QPalette.ColorRole.Text: "#1f2937",
        QPalette.ColorRole.Button: "#e8eef3",
        QPalette.ColorRole.ButtonText: "#243746",
        QPalette.ColorRole.Highlight: "#527b98",
        QPalette.ColorRole.HighlightedText: "#ffffff",
        QPalette.ColorRole.PlaceholderText: "#64748b",
    }
    for role, value in colors.items():
        palette.setColor(role, QColor(value))
    app.setPalette(palette)
    font = app.font()
    font.setWeight(QFont.Weight.Medium)
    app.setFont(font)


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("IVA Downloader")
    apply_light_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()
