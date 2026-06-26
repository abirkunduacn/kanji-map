import importlib.util
import pytest

playwright_missing = importlib.util.find_spec("playwright") is None

@pytest.mark.skipif(playwright_missing, reason="playwright not installed")
def test_pdf_path_naming():
    from pdf import generate_pdf
    assert generate_pdf.pdf_path("N4").name == "kanji-N4.pdf"
    assert generate_pdf.pdf_path("N5").parent.name == "pdf"
