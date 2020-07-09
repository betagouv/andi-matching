"""
Test des fixtures
"""


def test_source_tree(source_tree):
    assert (source_tree / "setup.py").is_file()


def test_data_directory(data_directory):
    assert data_directory.is_dir()
