import pytest
from graids_demo.formatting import edited_destination_content, split_text


def test_edit_uses_non_pinging_labels():
    result = edited_destination_content("updated", ("Example Raid", "Second Raid"))
    assert result == "[Example Raid] [Second Raid]\nupdated"
    assert "<@&" not in result


def test_split_text_respects_limit_and_natural_boundaries():
    text = "alpha beta gamma delta epsilon zeta eta theta"
    chunks = split_text(text, 12)
    assert all(0 < len(chunk) <= 12 for chunk in chunks)
    assert "".join(chunks).replace(" ", "") == text.replace(" ", "")


def test_split_text_requires_positive_limit():
    with pytest.raises(ValueError):
        split_text("abc", 0)
