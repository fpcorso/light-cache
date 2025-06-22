import os

import pytest

from src.simple_cache.cacher import Cacher


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
