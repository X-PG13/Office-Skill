from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

from office_skill.geometry import audit_slide, emu
from office_skill.patterns import text_problems
from scripts.qa.checks import placeholder_issues


def test_placeholder_patterns():
    assert text_problems("See the TODO before sending")
    assert text_problems("lorem ipsum dolor")
    assert text_problems("此处待填写")
    assert not text_problems("Section 1")


def test_gate_sees_a_placeholder_in_a_deck(tmp_path: Path):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    shape = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
    shape.text_frame.text = "TODO write the finding"
    path = tmp_path / "bad.pptx"
    prs.save(path)
    from scripts.qa.checks import extract_text

    assert placeholder_issues(extract_text(path))


def test_out_of_bounds_shape_fails_audit():
    prs = Presentation()
    prs.slide_width = emu(13.3333333333)
    prs.slide_height = emu(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_textbox(Inches(12), Inches(1), Inches(3), Inches(1))
    issues = audit_slide(slide, int(prs.slide_width), int(prs.slide_height))
    assert any("outside" in item for item in issues)
