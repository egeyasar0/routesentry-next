from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_action_metadata_contains_required_wrapper_contract():
    action = ROOT / "action.yml"

    assert action.exists()
    text = action.read_text(encoding="utf-8")
    for expected in ("path:", "format:", "output:", "fail-on:"):
        assert expected in text
    assert "using: composite" in text
    assert "python -m routesentry_next scan" in text
