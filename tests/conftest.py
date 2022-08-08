from pathlib import Path

import pytest


@pytest.fixture
def sample_dir():
    return Path(__file__).parent / "sample"
