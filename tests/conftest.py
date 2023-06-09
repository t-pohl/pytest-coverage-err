from dataclasses import dataclass
from glob import glob
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pytest_docker.plugin import Services
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from backend.application import app  # noqa
from backend.database import Base
from backend.settings import settings


# The next function and assignment are needed to import all the fixtures defined in the fixture folder,
# allowing better separation between different categories of fixtures.
def refactor(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")


pytest_plugins = [
    refactor(fixture) for fixture in glob("tests/fixtures/*.py") if "__" not in fixture
]


@pytest.hookimpl(hookwrapper=True)  # type: ignore
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, None]:
    outcome = yield
    report = outcome.get_result()

    if item.config.getoption("--no-skips") and call.excinfo:
        if report.skipped and call.excinfo.errisinstance(pytest.skip.Exception):
            report.outcome = "failed"
            r = call.excinfo._getreprcrash()  # noqa
            report.longrepr = f"Forbidden skipped test - {r.message}"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-skips",
        action="store_true",
        default=False,
        help="Skipping tests is not allowed",
    )


@pytest.fixture
def init_docker_postgres(docker_ip: str, docker_services: Services) -> None:
    """Ensures proper initialization of the postgres in docker compose.

    Args:
        docker_ip: The IP of the docker api (will be injected by
            pytest-docker).
        docker_services: The docker api (will be injected by pytest-docker).
    """

    uri = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.5, check=lambda: _is_postgres_ready(uri)
    )
    init_schemas_for_test(uri)


def _is_postgres_ready(uri: str) -> bool:
    try:
        create_engine(uri).connect()
    except:
        return False
    return True


def init_schemas_for_test(database_uri: str) -> None:
    """Creates all schemas that were added on the global declarative base.

    This only works if all database models are imported, because on loading
    the module the ORM classes are adding themselves to the global declarative
    base. This makes it very easy to set up the database in the tests always
    aligned to the current state.
    """

    engine = create_engine(database_uri)
    Base.metadata.reflect(bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest_asyncio.fixture
async def test_app(init_docker_postgres: None) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@dataclass
class TestDbSessions:
    """Wrapper for handing async session and sync probing session over to tests.

    Attributes:
        Async: The async session that is also used within the full app.
            Therefore this is the session that is put under test to see whether
            it is behaving exactly as expected.
        Probe: An independent probe session that can be used for setting
            up the test environment prior the test execution itself or probing
            for an expected result after a test execution occurred and the
            expected result should be asserted. It is important to not reuse the
            same functionality for probing and test setup that is also used for
            test execution itself, because this can lead to false positives.
    """

    Async: sessionmaker
    Probe: sessionmaker
    # ignore this class by pytest even though it starts with "Test"
    __test__: bool = False


@pytest_asyncio.fixture
async def postgres_sessionmakers(
    init_docker_postgres: None,
) -> AsyncGenerator[TestDbSessions, None]:
    """Provides a connection to the docker compose postgres for tests.

    This decorator sets up a connection to the postgres database from the docker
    compose file with pytest docker and wraps an async engine as well as a probe
    connection (for checking whether the test changed the database in the
    expected manner in an independent way) for test functions.

    Args:
        docker_ip: The IP of the docker service provided by pytest docker.
        docker_services: The docker service provided by pytest docker.

    Yields:
        A TestDbSessions containing the async engine used for the test and a
        probe to evaluate whether the test yielded the expected result. After
        the test execution the probe session is automatically closed.
    """

    async_uri = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    sync_uri = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    SyncSessionMaker = sessionmaker(
        bind=create_engine(sync_uri),
        class_=Session,
        expire_on_commit=False,
    )
    AsyncSessionMaker = sessionmaker(
        bind=create_async_engine(async_uri, poolclass=NullPool),
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield TestDbSessions(Async=AsyncSessionMaker, Probe=SyncSessionMaker)
