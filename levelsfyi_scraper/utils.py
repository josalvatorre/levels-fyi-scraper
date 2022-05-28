import itertools
from typing import Callable, Generator, Iterable, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


def trail(
    iterable: Iterable[T],
    trail_value: U = None,
) -> Generator[Union[T, U], None, None]:
    yield from iterable
    yield from itertools.cycle([trail_value])
    pass


def take_first(iterable: Iterable[T], amount: int) -> Generator[T, None, None]:
    iterator = iter(iterable)
    for _ in range(amount):
        try:
            yield next(iterator)
        except StopIteration:
            return
    pass


def if_error(function: Callable[[], T], substitute: U = None) -> Union[T, U]:
    try:
        return function()
    except Exception as e:
        print(f"caught {e}")
        return substitute
