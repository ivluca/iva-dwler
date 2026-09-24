from PySide6.QtGui import QColor, QFont

from iva_downloader import app


def test_apply_light_theme_forces_fusion_palette_and_medium_font(qapp):
    app.apply_light_theme(qapp)

    assert qapp.style().objectName().lower() == "fusion"
    assert qapp.palette().window().color() == QColor("#f4f6f8")
    assert qapp.palette().windowText().color() == QColor("#1f2937")
    assert qapp.font().weight() == QFont.Weight.Medium
