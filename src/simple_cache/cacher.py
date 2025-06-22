import datetime
import pickle


class Cacher:
    def __init__(self, namespace: str = 'general_cache', cache_directory: str = '.cache'):
        self.namespace = namespace
        self.cache_directory = cache_directory

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
        filename = f"{self.cache_directory}/{self.namespace}.pkl" if self.cache_directory and self.cache_directory != '.' else f"{self.namespace}.pkl"
        return filename