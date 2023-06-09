import json
import string
from datetime import datetime, timedelta, timezone
from enum import Enum
from random import choice, randint, random, seed
from typing import Any, Callable, Coroutine, Optional, Type, TypeVar
from uuid import UUID, uuid4

from httpretty import HTTPrettyRequestEmpty
from httpx import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.schemas import Message
from backend.utils.json_encoder import CustomEncoder
from tests.random_seed import test_seed

# TODO: Split up this file


T = TypeVar("T", bound=BaseModel)
U = TypeVar("U")
V = TypeVar("V")

seed(test_seed)


def schema_to_content(obj: T) -> str:
    return json.dumps(obj.dict(), default=str)


def parse_response(cls: Type[T], response: Response) -> T:
    return cls.parse_obj(response.json())


def parse_request(cls: Type[T], request: HTTPrettyRequestEmpty) -> T:
    return cls.parse_raw(request.body)


def schema_to_json_payload(create_schema: T) -> Any:
    return json.loads(json.dumps(create_schema.dict(), cls=CustomEncoder))


async def checked_request(
    request: Coroutine[Any, Any, Response], cls: Type[T], code: int = 200
) -> T:
    response = await request
    assert response.status_code == code
    return parse_response(cls, response)


async def check_success_msg(request: Coroutine[Any, Any, Response]) -> None:
    message = await checked_request(request, Message)
    assert message.message == "Success"


async def checked_page_elements(
    request: Coroutine[Any, Any, Response], cls: Type[T], code: int = 200
) -> list[T]:
    response = await request
    assert response.status_code == code
    response_json = response.json()
    assert "items" in response_json
    assert "total" in response_json
    assert "page" in response_json
    assert "size" in response_json
    return [cls.parse_obj(item) for item in response_json["items"]]


def rand_str(length: int = 10) -> str:
    possible_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(choice(possible_chars) for _ in range(length))


def rand_bool() -> bool:
    return choice([False, True])


def rand_uuid() -> UUID:
    return uuid4()


def rand_opt(v: U) -> Optional[U]:
    return choice([v, None])


def rand_float(max_: float = 1000, min_: float = 0) -> float:
    return min_ + random() * (max_ - min_)


def rand_int(max_: int = 1000, min_: int = 0) -> int:
    return randint(min_, max_)


def rand_enum(enum: Type[Enum]) -> Any:
    return choice(list(map(lambda v: v.value, list(enum))))  # type: ignore


def rand_list(generator: Callable[[], U], max_length: int = 10) -> list[U]:
    length = rand_int(min_=0, max_=max_length)
    """Takes a generator function and returns a list of generated results."""
    return [generator() for i in range(length)]


def rand_datetime(
    start_date: datetime = datetime(year=1990, month=1, day=1, tzinfo=timezone.utc),
    end_date: datetime = datetime(year=2040, month=1, day=1, tzinfo=timezone.utc),
) -> datetime:
    delta = end_date - start_date
    random_seconds = randint(0, int(delta.total_seconds()))
    random_time = start_date + timedelta(seconds=random_seconds)
    return random_time


def rand_dict(
    key_gen: Callable[[], U], value_gen: Callable[[], V], max_size: int = 10
) -> dict[Any, Any]:
    size = rand_int(min_=0, max_=max_size)
    result = dict()
    for i in range(size):
        result[key_gen()] = value_gen()

    return result


def rand_gen_or(gen_list: list[Callable[[], Any]]) -> Callable[[], Any]:
    """Return a new generator which each time randomly evaluates one of the input generators."""

    def return_function() -> Any:
        return choice(gen_list)()

    return return_function


def add_commit_refresh(db: Session, db_model: Any) -> None:
    """Sync way to create an entity in the DB. Should only be used in the tests."""
    db.add(db_model)
    db.commit()
    db.refresh(db_model)


def assert_numeric_equality(a: float, b: float, epsilon: float = 10**-5) -> None:
    """Assert equality within a certain range."""
    diff = abs(a - b)
    assert diff < epsilon
