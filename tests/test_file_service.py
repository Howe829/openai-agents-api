import pytest
from services.file import FileService


@pytest.fixture
def test_files(patch_engine):
    files = []
    for i in range(10):
        files.append(
            FileService.create_file(
                f"Name-{i}", path="test.pdf", size=10, content_type="application/pdf"
            )
        )
    return files


@pytest.fixture
def test_file(patch_engine):
    return FileService.create_file(
        "test_file", path="test.pdf", size=10, content_type="application/pdf"
    )


def test_get_files(test_files):
    files = FileService.get_files(per_page=5)
    assert len(files) == 5


@pytest.mark.parametrize(
    "name, expected_name ",
    [
        (None, "test_file"),
        ("updated_name", "updated_name"),
    ],
)
def test_update_file(test_file, name, expected_name):
    file = FileService.update_file(test_file.id, name)
    assert file.name == expected_name


def test_delete_file(test_file):
    FileService.delete_file(test_file.id)
    assert FileService.get_file(test_file.id) == None
