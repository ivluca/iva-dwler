import sys

from iva_downloader.app import main


def test_main_creates_window_and_exits_cleanly(qtbot):
    from iva_downloader.ui import MainWindow
    from unittest.mock import patch

    with patch.object(MainWindow, "show"):
        # main() calls app.exec() which blocks; patch it to return immediately
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        with patch.object(app.__class__, "exec", return_value=0):
            result = main()
    assert result == 0
