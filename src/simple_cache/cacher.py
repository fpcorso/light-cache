import datetime
import os
import pickle


class Cacher:
    def __init__(self, namespace: str = 'general_cache', cache_directory: str = '.cache'):
        self.namespace = namespace
        self.cache_directory = cache_directory

    def get_cached_item(self, key: str) -> dict | list | None:
        cache = self.load_cache()

        if key not in cache:
            return None

        if 'expires' not in cache[key] or cache[key]['expires'] < datetime.datetime.now():
            del cache[key]
            self.save_cache(cache)
            return None

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
        filename = self._get_file_from_type()
        try:
            with open(filename, 'wb') as cache_file:
                pickle.dump(data, cache_file)
        except Exception as e:
            print(f"Failed to write cache to file: {e}")

    def load_cache(self) -> dict:
        filename = self._get_file_from_type()
        try:
            with open(filename, 'rb') as cache_file:
                data = pickle.load(cache_file)
        except (FileNotFoundError, EOFError):
            data = {}

        return data

    def _get_file_from_type(self) -> str:
        if self.cache_directory and self.cache_directory != '.':
            filename = os.path.join(self.cache_directory, f"{self.namespace}.pkl")
        else:
            filename = f"{self.namespace}.pkl"

        return filename
