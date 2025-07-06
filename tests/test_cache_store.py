from datetime import datetime
import os
import shutil

import pytest

from src.light_cache import CacheStore


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache files and clean it up after tests."""
    cache_dir = os.path.join(os.getcwd(), "test_cache")
    os.makedirs(cache_dir, exist_ok=True)
    yield cache_dir
    shutil.rmtree(cache_dir)


def test_file_cache_basic_operations(temp_cache_dir):
    """Test basic file caching operations."""
    cache = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=False,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )

    test_data = {"key": "value"}
    cache.put("test_key", test_data)

    # Verify file exists
    cache_file = os.path.join(temp_cache_dir, "test_cache.json")
    assert os.path.exists(cache_file)

    # Verify data can be retrieved
    retrieved_data = cache.get("test_key")
    assert retrieved_data == test_data


def test_file_cache_persistence(temp_cache_dir):
    """Test that cached data persists between cacher instances."""
    # First instance caches data
    cacher1 = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=True,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )
    cacher1.put("test_key", {"data": "value"})

    # The second instance should be able to read the cached data
    cacher2 = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=True,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )
    retrieved = cacher2.get("test_key")
    assert retrieved == {"data": "value"}


def test_handle_corrupted_cache_file(temp_cache_dir):
    """Test handling of corrupted cache files."""
    cache_file = os.path.join(temp_cache_dir, "test_cache.json")

    # Create a corrupted cache file
    with open(cache_file, "w") as f:
        f.write("{ invalid json")

    cache = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=False,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )

    # Should handle the corrupted file gracefully
    data = cache.load_cache()
    assert isinstance(data, dict)
    assert len(data) == 0


def test_mixed_mode_operations(temp_cache_dir):
    """Test operations when both memory and disk caching are enabled."""
    cache = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=True,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )

    # Cache an item
    cache.put("test_key", {"data": "value"})

    # Verify it's in memory
    assert "test_key" in cache.load_cache()

    # Verify it's on disk
    cache_file = os.path.join(temp_cache_dir, "test_cache.json")
    assert os.path.exists(cache_file)


def test_memory_cache_and_retrieve_item():
    """Test basic caching and retrieval when using memory-only cache."""
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)
    test_data = {"key": "value"}

    # Cache the item
    cache.put("test_key", test_data)

    # Retrieve the item
    retrieved_data = cache.get("test_key")

    assert retrieved_data == test_data
    # Verify it's stored in memory
    assert "test_key" in cache.cache
    assert cache.cache["test_key"]["data"] == test_data


def test_memory_cache_multiple_items():
    """Test handling multiple items in the memory cache."""
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)
    items = {
        "key1": {"data": "value1"},
        "key2": {"data": "value2"},
        "key3": {"data": "value3"},
    }

    # Cache multiple items
    for key, value in items.items():
        cache.put(key, value)

    # Verify all items are stored and retrievable
    for key, value in items.items():
        retrieved = cache.get(key)
        assert retrieved == value


def test_memory_cache_overwrites():
    """Test that caching with the same key overwrites the previous value."""
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)

    # Cache initial data
    cache.put("test_key", {"version": 1})

    # Cache new data with the same key
    cache.put("test_key", {"version": 2})

    # Verify only new data is present
    retrieved = cache.get("test_key")
    assert retrieved == {"version": 2}


def test_memory_cache_clear_on_init():
    """Test that the memory cache starts fresh with each instance."""
    # First instance
    cacher1 = CacheStore(persist_cache=False, keep_cache_in_memory=True)
    cacher1.put("test_key", {"data": "value"})

    # Second instance should have empty cache
    cacher2 = CacheStore(persist_cache=False, keep_cache_in_memory=True)
    assert cacher2.get("test_key") is None


def test_memory_cache_nonexistent_key():
    """Test retrieving non-existent key from the memory cache."""
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)

    retrieved = cache.get("nonexistent")
    assert retrieved is None


def test_has_with_existing_key():
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)
    test_data = {"test": "value"}
    cache.put("test_key", test_data)

    assert cache.has("test_key") is True


def test_has_with_nonexistent_key():
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)

    assert cache.has("nonexistent_key") is False


def test_forget_existing_item():
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)

    # Cache an item
    cache.put("test_key", {"data": "value"})

    # Verify it exists
    assert cache.has("test_key") is True

    # Forget it
    result = cache.forget("test_key")

    # Verify it was forgotten
    assert result is True
    assert cache.has("test_key") is False
    assert cache.get("test_key") is None


def test_forget_nonexistent_item():
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)

    # Try to forget non-existent item
    result = cache.forget("nonexistent")

    assert result is False


def test_pull_existing_item():
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)
    test_data = {"key": "value"}

    # Cache an item
    cache.put("test_key", test_data)

    # Pull the item
    pulled_data = cache.pull("test_key")

    # Verify pulled data matches original
    assert pulled_data == test_data
    # Verify the item was removed
    assert cache.has("test_key") is False


def test_pull_nonexistent_item():
    cache = CacheStore(persist_cache=False, keep_cache_in_memory=True)

    # Try to pull the non-existent item
    default_value = {"default": "value"}
    pulled_data = cache.pull("nonexistent", default=default_value)

    # Verify default value is returned
    assert pulled_data == default_value


def test_pull_persistence(temp_cache_dir):
    # Create the cache with both memory and file persistence
    cache = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=True,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )

    test_data = {"key": "value"}
    cache.put("test_key", test_data)

    # Pull the item
    pulled_data = cache.pull("test_key")

    # Verify pulled data matches original
    assert pulled_data == test_data

    # Create new cache instance to verify item was removed from the file
    new_cache = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=True,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )

    # Verify the item doesn't exist in the new instance
    assert new_cache.has("test_key") is False


def test_pull_without_memory_cache(temp_cache_dir):
    cache = CacheStore(
        persist_cache=True,
        keep_cache_in_memory=False,
        store="test_cache",
        cache_directory=temp_cache_dir,
    )

    test_data = {"key": "value"}
    cache.put("test_key", test_data)

    # Pull the item
    pulled_data = cache.pull("test_key")

    # Verify pulled data matches original
    assert pulled_data == test_data
    # Verify the item was removed
    assert cache.has("test_key") is False


def test_is_cache_directory_needed_with_valid_directory():
    cache = CacheStore(persist_cache=False, store="test", cache_directory="test_dir")
    assert cache._is_cache_directory_needed() is True


def test_is_cache_directory_needed_with_dot_directory():
    cache = CacheStore(persist_cache=False, store="test", cache_directory=".")
    assert cache._is_cache_directory_needed() is False


def test_is_cache_directory_needed_with_none_directory():
    cache = CacheStore(persist_cache=False, store="test", cache_directory=None)
    assert cache._is_cache_directory_needed() is False


def test_is_cache_directory_needed_with_empty_directory():
    cache = CacheStore(persist_cache=False, store="test", cache_directory="")
    assert cache._is_cache_directory_needed() is False


def test_is_expired_with_future_expiration():
    future_time = int(datetime.now().timestamp()) + 3600
    item = {"data": "test", "expires": future_time}
    assert CacheStore._is_expired(item) is False


def test_is_expired_with_past_expiration():
    past_time = int(datetime.now().timestamp()) - 3600
    item = {"data": "test", "expires": past_time}
    assert CacheStore._is_expired(item) is True


def test_is_expired_with_no_expiration():
    """Test that items with None expiration never expire"""
    item = {"expires": None, "data": "test"}
    assert CacheStore._is_expired(item) is False


@pytest.mark.parametrize(
    "invalid_item",
    [
        {"expires": "not a timestamp"},  # String instead of int
        {"expires": []},  # List
        None,  # None instead of dict
        [],  # List instead of dict
        "string",  # String instead of dict
        {},  # Empty dict
        {"data": "test"},  # Missing expires key
    ],
)
def test_is_expired_with_invalid_items(invalid_item):
    """Test that invalid items are considered expired"""
    assert CacheStore._is_expired(invalid_item) is True


def test_get_cache_path_with_directory():
    """Test cache path generation with a directory"""
    cache = CacheStore(
        persist_cache=False, store="test_cache", cache_directory="cache_dir"
    )
    expected = os.path.join("cache_dir", "test_cache.json")
    assert cache._get_cache_path() == expected


def test_get_cache_path_without_directory():
    """Test cache path generation with no directory (None)"""
    cache = CacheStore(persist_cache=False, store="test_cache", cache_directory=None)
    assert cache._get_cache_path() == "test_cache.json"


def test_get_cache_path_with_dot_directory():
    """Test cache path generation with the '.' directory"""
    cache = CacheStore(persist_cache=False, store="test_cache", cache_directory=".")
    assert cache._get_cache_path() == "test_cache.json"


def test_get_cache_path_with_empty_directory():
    """Test cache path generation with an empty string directory"""
    cache = CacheStore(persist_cache=False, store="test_cache", cache_directory="")
    assert cache._get_cache_path() == "test_cache.json"


def test_get_cache_path_with_nested_directory():
    """Test cache path generation with a nested directory path"""
    nested_path = os.path.join("path", "to", "cache")
    cache = CacheStore(
        persist_cache=False, store="test_cache", cache_directory=nested_path
    )
    expected = os.path.join("path", "to", "cache", "test_cache.json")
    assert cache._get_cache_path() == expected


def test_basic_filename():
    """Test basic valid filename sanitization."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_store("test") == "test"
    assert cache._sanitize_store("test-file") == "test-file"
    assert cache._sanitize_store("test_file") == "test_file"


def test_remove_path_components():
    """Test removal of path components."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_store("../test") == "test"
    assert cache._sanitize_store("/etc/passwd") == "passwd"
    assert cache._sanitize_store("folder/subfolder/file") == "file"


def test_remove_special_chars():
    """Test removal of special characters."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_store("test!@#$%^&*()") == "test"
    assert cache._sanitize_store("hello world") == "helloworld"
    assert cache._sanitize_store("file.txt") == "filetxt"
    assert cache._sanitize_store("$pecial.file.name") == "pecialfilename"


def test_empty_or_invalid_input():
    """Test handling of empty or invalid input."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_store("") == "general_cache"
    assert cache._sanitize_store("...") == "general_cache"
    assert cache._sanitize_store("   ") == "general_cache"
    assert cache._sanitize_store("#@!") == "general_cache"


def test_valid_directory():
    """Test valid directory paths."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_directory("test_dir") == "test_dir"
    assert cache._sanitize_directory("./test_dir") == "test_dir"

    sub_path = os.path.join("test_dir", "subdir")
    assert cache._sanitize_directory(sub_path) == sub_path


def test_current_directory():
    """Test current directory handling."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_directory(".") == "."
    assert cache._sanitize_directory("") == "."


def test_parent_directory_traversal():
    """Test parent directory traversal prevention."""
    cache = CacheStore(persist_cache=False)
    assert cache._sanitize_directory("../outside") == ".cache"
    assert cache._sanitize_directory("../../outside") == ".cache"
    assert cache._sanitize_directory("test_dir/../../outside") == ".cache"


def test_absolute_paths():
    """Test absolute path handling."""
    cache = CacheStore(persist_cache=False)
    # Should reject absolute paths outside CWD
    assert cache._sanitize_directory("/tmp") == ".cache"
    assert cache._sanitize_directory("/etc") == ".cache"

    # Should allow absolute paths that resolve inside CWD
    cwd = os.getcwd()
    test_dir_path = os.path.join(cwd, "test_dir")
    assert cache._sanitize_directory(test_dir_path) == "test_dir"
