"""Dashboard smoke tests (skipped when Streamlit is unavailable)."""

import os

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

APP = os.path.join(os.path.dirname(__file__), "..", "app.py")


def test_dashboard_runs_without_exception():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception


def test_dashboard_has_three_tabs():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception
    assert len(at.tabs) == 3
