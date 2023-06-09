import pytest
import pytest_asyncio
from httpx import AsyncClient

from backend.api.schemas import AssetCreate, AssetPairCreate
from tests.api.test_03_asset import create_asset


@pytest.fixture
def asset_create1() -> AssetCreate:
    return AssetCreate(name="SynCoin", short_name="SYC", type="crypto")


@pytest.fixture
def asset_create2() -> AssetCreate:
    return AssetCreate(name="Mayan gold", short_name="MG", type="ancient")


@pytest.fixture
def asset_create3() -> AssetCreate:
    return AssetCreate(name="Bitcoin", short_name="BTC", type="crypto")


@pytest.fixture
def asset_create4() -> AssetCreate:
    return AssetCreate(name="Asset4", short_name="A4", type="crypto")


@pytest.fixture
def asset_create5() -> AssetCreate:
    return AssetCreate(name="Asset5", short_name="A5", type="crypto")


@pytest.fixture
def asset_create6() -> AssetCreate:
    return AssetCreate(name="Asset5", short_name="A6", type="crypto")


@pytest.fixture
def asset_create_list1(asset_create1: AssetCreate) -> list[AssetCreate]:
    return [asset_create1]


@pytest.fixture
def asset_create_list2(
    asset_create1: AssetCreate, asset_create2: AssetCreate
) -> list[AssetCreate]:
    return [asset_create1, asset_create2]


@pytest.fixture
def asset_create_list3(
    asset_create1: AssetCreate, asset_create2: AssetCreate, asset_create3: AssetCreate
) -> list[AssetCreate]:
    return [asset_create1, asset_create2, asset_create3]


@pytest_asyncio.fixture
async def asset_pair_create1(
    test_app: AsyncClient,
    asset_create1: AssetCreate,
    asset_create2: AssetCreate,
) -> AssetPairCreate:
    base_asset = await create_asset(test_app, asset_create1)
    quote_asset = await create_asset(test_app, asset_create2)
    return AssetPairCreate(base_id=base_asset.id, quote_id=quote_asset.id)


@pytest_asyncio.fixture
async def asset_pair_create2(
    test_app: AsyncClient,
    asset_create3: AssetCreate,
    asset_create4: AssetCreate,
) -> AssetPairCreate:
    base_asset = await create_asset(test_app, asset_create3)
    quote_asset = await create_asset(test_app, asset_create4)
    return AssetPairCreate(base_id=base_asset.id, quote_id=quote_asset.id)


@pytest_asyncio.fixture
async def asset_pair_create3(
    test_app: AsyncClient,
    asset_create5: AssetCreate,
    asset_create6: AssetCreate,
) -> AssetPairCreate:
    base_asset = await create_asset(test_app, asset_create5)
    quote_asset = await create_asset(test_app, asset_create6)
    return AssetPairCreate(base_id=base_asset.id, quote_id=quote_asset.id)


@pytest.fixture
def asset_pair_create_list1(
    asset_pair_create1: AssetPairCreate,
) -> list[AssetPairCreate]:
    return [asset_pair_create1]


@pytest.fixture
def asset_pair_create_list2(
    asset_pair_create1: AssetPairCreate, asset_pair_create2: AssetPairCreate
) -> list[AssetPairCreate]:
    return [asset_pair_create1, asset_pair_create2]


@pytest.fixture
def asset_pair_create_list3(
    asset_pair_create1: AssetPairCreate,
    asset_pair_create2: AssetPairCreate,
    asset_pair_create3: AssetPairCreate,
) -> list[AssetPairCreate]:
    return [asset_pair_create1, asset_pair_create2, asset_pair_create3]
