import pytest

from app.main import create_app
from app.pipeline import compute
from app.source import receive


@pytest.fixture
def files():
    return receive({'sample':'dirty'})


@pytest.fixture
def dirty(files):
    return compute(files)


@pytest.fixture
def client(tmp_path):
    return create_app(tmp_path/'cabinet').test_client()
