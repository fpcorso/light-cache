from datetime import datetime, timedelta
import os

import pytest

from src.simple_cache import Cacher


def test_is_cache_directory_needed_with_valid_directory():
    cacher = Cacher(namespace='test', cache_directory='test_dir')
    assert cacher._is_cache_directory_needed() is True

def test_is_cache_directory_needed_with_dot_directory():
    cacher = Cacher(namespace='test', cache_directory='.')
    assert cacher._is_cache_directory_needed() is False

def test_is_cache_directory_needed_with_none_directory():
    cacher = Cacher(namespace='test', cache_directory=None)
    assert cacher._is_cache_directory_needed() is False

def test_is_cache_directory_needed_with_empty_directory():
    cacher = Cacher(namespace='test', cache_directory='')
    assert cacher._is_cache_directory_needed() is False

def test_is_expired_with_no_expiration():
    item = {'data': 'test'}
    assert Cacher._is_expired(item) is True

def test_is_expired_with_future_expiration():
    future_time = datetime.now() + timedelta(hours=1)
    item = {'data': 'test', 'expires': future_time}
    assert Cacher._is_expired(item) is False

def test_is_expired_with_past_expiration():
    past_time = datetime.now() - timedelta(hours=1)
    item = {'data': 'test', 'expires': past_time}
    assert Cacher._is_expired(item) is True

@pytest.mark.parametrize("invalid_item", [
    {'expires': 'not a datetime'},  # String instead of datetime
    {'expires': None},              # None value
    {'expires': 123},               # Integer
    {'expires': []},                # List
    None,                           # None instead of dict
    [],                             # List instead of dict
    "string",                       # String instead of dict
    42,                            # Integer instead of dict
    {},                            # Empty dict
    {'data': 'test'},              # Missing expires key
])
def test_is_expired_with_invalid_items(invalid_item):
    """Test that invalid items are considered expired"""
    assert Cacher._is_expired(invalid_item) is True

def test_get_cache_path_with_directory():
    """Test cache path generation with a directory"""
    cacher = Cacher(namespace='test_cache', cache_directory='cache_dir')
    expected = os.path.join('cache_dir', 'test_cache.pkl')
    assert cacher._get_cache_path() == expected

def test_get_cache_path_without_directory():
    """Test cache path generation with no directory (None)"""
    cacher = Cacher(namespace='test_cache', cache_directory=None)
    assert cacher._get_cache_path() == 'test_cache.pkl'

def test_get_cache_path_with_dot_directory():
    """Test cache path generation with the '.' directory"""
    cacher = Cacher(namespace='test_cache', cache_directory='.')
    assert cacher._get_cache_path() == 'test_cache.pkl'

def test_get_cache_path_with_empty_directory():
    """Test cache path generation with an empty string directory"""
    cacher = Cacher(namespace='test_cache', cache_directory='')
    assert cacher._get_cache_path() == 'test_cache.pkl'

def test_get_cache_path_with_nested_directory():
    """Test cache path generation with a nested directory path"""
    nested_path = os.path.join('path', 'to', 'cache')
    cacher = Cacher(namespace='test_cache', cache_directory=nested_path)
    expected = os.path.join('path', 'to', 'cache', 'test_cache.pkl')
    assert cacher._get_cache_path() == expected
