# light-cache

A Python package for using disk-based or object-bashed caching, perfect for simple scripts or Jupyter Notebooks.

## Features

✨ **Flexible Storage Options**
- Multiple cache storage modes (Memory, Disk, or Hybrid)
- Support for multiple independent cache stores
- Configurable cache directory location

⚡ **Performance**
- In-memory caching for fast access
- Disk persistence for data durability
- Hybrid mode for optimal performance and reliability

⚙️ **Advanced Cache Control**
- Automatic cache expiration
- Manual cache item removal
- Configurable default values for cache misses
- Non-expiring cache items support

🛠️ **Developer Friendly**
- Simple, intuitive API
- Perfect for scripts and Jupyter notebooks
- No external dependencies
- Lightweight alternative to Redis for simple use cases


## Install

Use pip to install:

```shell
pip install light-cache
```

## Usage

To get started, you need to set up a cache store:

```python
from light_cache import CacheStore

cache = CacheStore(persist_cache=True, keep_cache_in_memory=True)
```

There are three main modes for this cache:

1. **Disk cache**: Setting `persist_cache` to True and `keep_cache_in_memory` to False, the cache will read and write to a local cache file on each get/put operation. If you have many instances of a script running and need to keep the cache in sync, this is likely the right option.
2. **Memory cache**: Setting `persist_cache` to False and `keep_cache_in_memory` to True, keeps the cache in memory during the execution of the script or while the notebook is running. The cache will not persist between sessions. If you do not need the cache to exist after the session ends and have many computationally intensive functions during the execution, this is likely the right option.
3. **Hybrid** (default and recommended): Setting both to True will allow the cache to stay in memory during execution but save changes to a file to persist between sessions. For most use-cases of working in a notebook or creating small scripts that do not require full Redis or similar cache, this is likely the right option.

### Using multiple stores

You can set up different cache stores for different information. For example, if you need one store for just movies and another for podcasts, you could:

```python
from light_cache import CacheStore

movie_cache = CacheStore(store='movies')
podcast_cache = CacheStore(store='podcasts')
```

### Setting and retrieving values

The main methods are `get()`, `put()`, `has()`, and `forget()`.

```python
from light_cache import CacheStore

cache = CacheStore()

cache.put('some-key', 'some-value')
my_value = cache.get('some-key')

# `get()` returns None if cache doesn't exist. This can be changed using the `default` parameter
my_value = cache.get('some-nonexistent-key', default=0)

if cache.has('some-key'):
    # do something

# `pull()` will retrieve a cached item and delete it from the cache if it exists
my_value = cache.pull('some-key')

# Expiration is in seconds (defaults to 5 minutes)
cache.put('new-key', 'new-value', expires=1200)

# Set to None for items that should not expire
cache.put('never-expire-key', 'never-expire-value', expires=None)

# Items that do not expire will remain in cache until the item is removed using `forget()`
cache.forget('never-expire-key')
```

### Change location of the cache directory

When using disk-based cache, the files are stored in `.cache/` but this can be changed:

```python
from light_cache import CacheStore

cache = CacheStore(cache_directory='src/app/cache')
```

## Contributing

Community made feature requests, patches, bug reports, and contributions are always welcome.

Please review [our contributing guidelines](https://github.com/fpcorso/light-cache/blob/main/CONTRIBUTING.md) if you decide to make a contribution.

### Setting up development environment

This project uses [Poetry](https://python-poetry.org/docs/) for managing dependencies and environments.

#### Tests 

This project uses [pytest](https://docs.pytest.org/en/stable/) for its tests.

To run tests locally, use:

```shell
poetry run pytest
```

#### Formatter

This project uses [black](https://black.readthedocs.io/en/stable/index.html) for formatting. To run the formatter, use:

```shell
poetry run black .
```

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/fpcorso/light-cache/blob/main/LICENSE) for more details.