from iva_downloader.resources import ICON_NAMES, icon, load_app_font, resource_path


def test_bundled_font_and_licenses_are_available():
    assert resource_path("fonts", "SNPro-Variable.ttf").is_file()
    assert resource_path("licenses", "SNPRO_OFL.txt").is_file()
    assert resource_path("licenses", "MATERIAL_SYMBOLS_LICENSE.txt").is_file()


def test_brand_font_loads_and_all_material_icons_are_valid(qapp):
    assert load_app_font() == "SN Pro"
    assert all(not icon(name).isNull() for name in ICON_NAMES)
