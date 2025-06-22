from datetime import datetime, timedelta
import os

import pytest

from src.simple_cache import Cacher


def test_is_cache_directory_needed_with_valid_directory():
    cacher = Cacher(persist_cache=False, namespace="test", cache_directory="test_dir")
    assert cacher._is_cache_directory_needed() is True


def test_is_cache_directory_needed_with_dot_directory():
    cacher = Cacher(persist_cache=False, namespace="test", cache_directory=".")
    assert cacher._is_cache_directory_needed() is False


def test_is_cache_directory_needed_with_none_directory():
    cacher = Cacher(persist_cache=False, namespace="test", cache_directory=None)
    assert cacher._is_cache_directory_needed() is False


def test_is_cache_directory_needed_with_empty_directory():
    cacher = Cacher(persist_cache=False, namespace="test", cache_directory="")
    assert cacher._is_cache_directory_needed() is False


def test_is_expired_with_no_expiration():
    item = {"data": "test"}
    assert Cacher._is_expired(item) is True


def test_is_expired_with_future_expiration():
    future_time = datetime.now() + timedelta(hours=1)
    item = {"data": "test", "expires": future_time}
    assert Cacher._is_expired(item) is False


def test_is_expired_with_past_expiration():
    past_time = datetime.now() - timedelta(hours=1)
    item = {"data": "test", "expires": past_time}
    assert Cacher._is_expired(item) is True


@pytest.mark.parametrize(
    "invalid_item",
    [
        {"expires": "not a datetime"},  # String instead of datetime
        {"expires": None},  # None value
        {"expires": 123},  # Integer
        {"expires": []},  # List
        None,  # None instead of dict
        [],  # List instead of dict
        "string",  # String instead of dict
        42,  # Integer instead of dict
        {},  # Empty dict
        {"data": "test"},  # Missing expires key
    ],
)
def test_is_expired_with_invalid_items(invalid_item):
    """Test that invalid items are considered expired"""
    assert Cacher._is_expired(invalid_item) is True


def test_get_cache_path_with_directory():
    """Test cache path generation with a directory"""
    cacher = Cacher(
        persist_cache=False, namespace="test_cache", cache_directory="cache_dir"
    )
    expected = os.path.join("cache_dir", "test_cache.json")
    assert cacher._get_cache_path() == expected


def test_get_cache_path_without_directory():
    """Test cache path generation with no directory (None)"""
    cacher = Cacher(persist_cache=False, namespace="test_cache", cache_directory=None)
    assert cacher._get_cache_path() == "test_cache.json"


def test_get_cache_path_with_dot_directory():
    """Test cache path generation with the '.' directory"""
    cacher = Cacher(persist_cache=False, namespace="test_cache", cache_directory=".")
    assert cacher._get_cache_path() == "test_cache.json"


def test_get_cache_path_with_empty_directory():
    """Test cache path generation with an empty string directory"""
    cacher = Cacher(persist_cache=False, namespace="test_cache", cache_directory="")
    assert cacher._get_cache_path() == "test_cache.json"


def test_get_cache_path_with_nested_directory():
    """Test cache path generation with a nested directory path"""
    nested_path = os.path.join("path", "to", "cache")
    cacher = Cacher(
        persist_cache=False, namespace="test_cache", cache_directory=nested_path
    )
    expected = os.path.join("path", "to", "cache", "test_cache.json")
    assert cacher._get_cache_path() == expected


def test_basic_filename():
    """Test basic valid filename sanitization."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_namespace("test") == "test"
    assert cacher._sanitize_namespace("test-file") == "test-file"
    assert cacher._sanitize_namespace("test_file") == "test_file"


def test_remove_path_components():
    """Test removal of path components."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_namespace("../test") == "test"
    assert cacher._sanitize_namespace("/etc/passwd") == "passwd"
    assert cacher._sanitize_namespace("folder/subfolder/file") == "file"
    assert cacher._sanitize_namespace("C:\\Windows\\file") == "file"


def test_remove_special_chars():
    """Test removal of special characters."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_namespace("test!@#$%^&*()") == "test"
    assert cacher._sanitize_namespace("hello world") == "helloworld"
    assert cacher._sanitize_namespace("file.txt") == "filetxt"
    assert cacher._sanitize_namespace("$pecial.file.name") == "pecialfilename"


def test_empty_or_invalid_input():
    """Test handling of empty or invalid input."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_namespace("") == "general_cache"
    assert cacher._sanitize_namespace("...") == "general_cache"
    assert cacher._sanitize_namespace("   ") == "general_cache"
    assert cacher._sanitize_namespace("#@!") == "general_cache"


def test_valid_directory():
    """Test valid directory paths."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_directory("test_dir") == "test_dir"
    assert cacher._sanitize_directory("./test_dir") == "test_dir"

    sub_path = os.path.join("test_dir", "subdir")
    assert cacher._sanitize_directory(sub_path) == sub_path


def test_current_directory():
    """Test current directory handling."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_directory(".") == "."
    assert cacher._sanitize_directory("") == "."


def test_parent_directory_traversal():
    """Test parent directory traversal prevention."""
    cacher = Cacher(persist_cache=False)
    assert cacher._sanitize_directory("../outside") == ".cache"
    assert cacher._sanitize_directory("../../outside") == ".cache"
    assert cacher._sanitize_directory("test_dir/../../outside") == ".cache"


def test_absolute_paths():
    """Test absolute path handling."""
    cacher = Cacher(persist_cache=False)
    # Should reject absolute paths outside CWD
    assert cacher._sanitize_directory("/tmp") == ".cache"
    assert cacher._sanitize_directory("/etc") == ".cache"

    # Should allow absolute paths that resolve inside CWD
    cwd = os.getcwd()
    test_dir_path = os.path.join(cwd, "test_dir")
    assert cacher._sanitize_directory(test_dir_path) == "test_dir"
