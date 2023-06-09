from typing import Callable, Generic, TypeVar

Key = TypeVar("Key")
Value = TypeVar("Value")


class Cache(Generic[Key, Value], dict[Key, Value]):
    factory: Callable[[Key], Value]

    def __init__(self, factory: Callable[[Key], Value]):
        super().__init__()
        self.factory = factory

    def __missing__(self, key: Key) -> Value:
        value = self.factory(key)
        self.__setitem__(key, value)
        return value
