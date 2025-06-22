import datetime
import logging
import os
import pickle

logger = logging.getLogger(__name__)


class Cacher:
    def __init__(self, namespace: str = 'general_cache', cache_directory: str = '.cache'):
        self.namespace = namespace
        self.cache_directory = cache_directory

    def get_cached_item(self, key: str) -> dict | list | None:
        cache = self.load_cache()

        if key not in cache:
            return None

        if self._is_expired(cache[key]):
            del cache[key]
            self.save_cache(cache)
            return None

        logger.debug(f"Cache hit for key: {key}")
        return cache[key]['data']

    def cache_item(self, key: str, item: dict | list, expires_in_hours: int = 24):
        cache = self.load_cache()

        prepared_item = {
            'expires': datetime.datetime.now() + datetime.timedelta(hours=expires_in_hours),
            'data': item
        }

        cache[key] = prepared_item
        self.save_cache(cache)

    def save_cache(self, data: dict) -> None:
        filename = self._get_cache_path()
        try:
            with open(filename, 'wb') as cache_file:
                pickle.dump(data, cache_file)
        except Exception as e:
            logger.error(f"Failed to write cache to file: {e}")

    def load_cache(self) -> dict:
        filename = self._get_cache_path()
        try:
            with open(filename, 'rb') as cache_file:
                data = pickle.load(cache_file)
        except (FileNotFoundError, EOFError):
            data = {}

        return data

    def _get_cache_path(self) -> str:
        if self.cache_directory and self.cache_directory != '.':
            filename = os.path.join(self.cache_directory, f"{self.namespace}.pkl")
        else:
            filename = f"{self.namespace}.pkl"

        return filename

    def _is_expired(self, item: dict) -> bool:
        return 'expires' not in item or item['expires'] < datetime.datetime.now()