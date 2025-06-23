import datetime
import logging
import os

from .JSONSerializer import JSONSerializer

logger = logging.getLogger(__name__)


class Cacher:
    """
    A flexible caching system that supports both in-memory and persistent file-based caching.

    This class provides functionality to cache data with optional expiration times,
    persistence to disk, and memory-only operations. It handles JSON serialization
    of cached data and provides methods for storing, retrieving, and managing cached items.

    Args:
        persist_cache (bool): Whether to save cache to disk. Defaults to True.
        keep_cache_in_memory (bool): Whether to maintain an in-memory cache. Defaults to True.
        store (str): Name of the cache store/file. Defaults to "general_cache".
        cache_directory (str): Directory to store cache files. Defaults to ".cache".
    """

    def __init__(
        self,
        persist_cache: bool = True,
        keep_cache_in_memory: bool = True,
        store: str = "general_cache",
        cache_directory: str = ".cache",
    ):
        self.persist_cache = persist_cache
        self.keep_cache_in_memory = keep_cache_in_memory
        self.store = self._sanitize_store(store)
        self.cache_directory = self._sanitize_directory(cache_directory)
        self.cache = {}

        # Make sure the cache directory exists if we need it.
        if self.persist_cache:
            self._ensure_cache_directory_exists()

        # Remove all expired items from the existing cache, if any.
        self.remove_expired_items()

        # If we are using object-caching, go ahead and load the cache in now to be used.
        if self.keep_cache_in_memory:
            self.cache = self.load_cache()

    def get(self, key: str, default=None) -> dict | list | None:
        """
        Retrieve an item from the cache.

        Args:
            key (str): The key to look up in the cache.
            default: Value to return if key is not found or expired. Defaults to None.

        Returns:
            The cached item if found and not expired, otherwise the default value.
        """
        cache = self.load_cache()

        if key not in cache:
            return default

        item = cache[key].copy()
        if self._is_expired(item):
            del cache[key]
            self.save_cache(cache)
            return default

        logger.debug(f"Cache hit for key: {key}")
        return item["data"]

    def put(self, key: str, item: dict | list, expires: int | None = 600):
        """
        Store an item in the cache.

        Args:
            key (str): The key under which to store the item.
            item (dict | list): The data to cache.
            expires (int | None): Time in seconds until the item expires.
                                None means the item never expires. Defaults to 600 seconds.
        """
        cache = self.load_cache()

        prepared_item = {
            "expires": (
                None
                if expires is None
                else int(datetime.datetime.now().timestamp()) + expires
            ),
            "data": item,
        }

        cache[key] = prepared_item
        self.save_cache(cache)

    def has(self, key: str) -> bool:
        """
        Check if a key exists in the cache and is not expired.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists and is not expired, False otherwise.
        """
        cache = self.load_cache()

        if key in cache:
            item = cache[key].copy()
            if self._is_expired(item):
                del cache[key]
                self.save_cache(cache)
            else:
                return True

        return False

    def forget(self, key: str) -> bool:
        """
        Remove an item from the cache.

        Args:
            key (str): The key to remove.

        Returns:
            bool: True if the key was found and removed, False otherwise.
        """
        cache = self.load_cache()
        if key in cache:
            del cache[key]
            self.save_cache(cache)
            return True
        return False

    def save_cache(self, data: dict) -> None:
        """
        Save the cache data to memory and/or disk based on configuration.

        Args:
            data (dict): The cache data to save.
        """
        if self.keep_cache_in_memory:
            self.cache = data

        if self.persist_cache:
            filename = self._get_cache_path()
            try:
                with open(filename, "w") as cache_file:
                    cached_data = JSONSerializer().encode(data)
                    cache_file.write(cached_data)
            except Exception as e:
                logger.error(f"Failed to write cache to file: {e}")

    def load_cache(self) -> dict:
        """
        Load the cache from memory or disk based on configuration.

        Returns:
            dict: The loaded cache data.
        """
        if self.keep_cache_in_memory:
            return self.cache

        filename = self._get_cache_path()
        try:
            with open(filename, "r") as cache_file:
                cached_data = cache_file.read()
                data = JSONSerializer().decode(cached_data)
        except (FileNotFoundError, EOFError):
            data = {}

        return data

    def remove_expired_items(self):
        """Remove all expired items from the cache."""
        cache = self.load_cache()

        expired = [k for k, v in cache.items() if self._is_expired(v)]
        for key in expired:
            del cache[key]

        self.save_cache(cache)

    def _get_cache_path(self) -> str:
        if self._is_cache_directory_needed():
            filename = os.path.join(self.cache_directory, f"{self.store}.json")
        else:
            filename = f"{self.store}.json"

        return filename

    def _ensure_cache_directory_exists(self) -> None:
        if not self._is_cache_directory_needed():
            return

        try:
            os.makedirs(self.cache_directory, mode=0o700, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create cache directory: {e}")

    def _is_cache_directory_needed(self) -> bool:
        return bool(self.cache_directory) and self.cache_directory != "."

    @staticmethod
    def _sanitize_store(store: str) -> str:
        """Sanitize the store by removing path traversal components and invalid chars."""
        # Remove any directory traversal attempt
        base_store = os.path.basename(store)

        # Only allow alphanumeric chars, underscore, and hyphen
        sanitized = "".join(c for c in base_store.lower() if c.isalnum() or c in "_-")

        if not sanitized:
            logger.warning("Empty filename after sanitization.")
            sanitized = "general_cache"

        return sanitized

    @staticmethod
    def _sanitize_directory(directory: str) -> str:
        """Sanitize the directory path by resolving to the absolute path and checking traversal."""
        if not directory or directory == ".":
            return "."

        # Convert to the absolute path and resolve any symlinks
        abs_path = os.path.abspath(directory)
        real_path = os.path.realpath(abs_path)

        # Ensure the directory is within the current working directory
        cwd = os.path.realpath(os.getcwd())
        if not real_path.startswith(cwd):
            logger.warning(
                f"Attempted directory traversal outside CWD. Defaulting to '.cache'"
            )
            return ".cache"

        # Convert back to the relative path from CWD
        try:
            relative_path = os.path.relpath(real_path, cwd)
            return relative_path if relative_path != "." else ".cache"
        except ValueError:
            # Handle any path resolution errors
            logger.warning("Error resolving relative path. Defaulting to '.cache'")
            return ".cache"

    @staticmethod
    def _is_expired(item: dict) -> bool:
        """
        Check if a cache item is expired.
        Returns True if:
        - item is not a dict
        - 'expires' key is missing
        - 'expires' value is not an integer timestamp or None
        - expiration time is in the past
        """
        if not isinstance(item, dict):
            return True

        if "expires" not in item:
            return True

        try:
            expiration = item["expires"]

            # If never expires
            if expiration is None:
                return False
            # If is invalid, consider it expired
            if not isinstance(expiration, int):
                return True
            return expiration < int(datetime.datetime.now().timestamp())
        except Exception:
            # Catch any comparison errors or other unexpected issues
            return True
