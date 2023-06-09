import uuid

import pytest
from httpx import AsyncClient

from backend.api.schemas import (Asset, AssetCreate, AssetPair,
                                 AssetPairCreate, Message)
from tests.utils import (checked_page_elements, checked_request,
                         schema_to_json_payload)


async def create_asset(test_app: AsyncClient, asset_create: AssetCreate) -> Asset:
    return await checked_request(
        test_app.post("/assets/", json=schema_to_json_payload(asset_create)), Asset
    )


@pytest.mark.asyncio
@pytest.mark.dependency(name="create_asset")
async def test_create_asset(test_app: AsyncClient, asset_create1: AssetCreate) -> None:
    asset = await create_asset(test_app, asset_create1)
    assert asset.name == asset_create1.name
    assert asset.short_name == asset_create1.short_name
    assert asset.type == asset_create1.type


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset"])
async def test_create_asset_duplicate(
    test_app: AsyncClient, asset_create1: AssetCreate
) -> None:
    await create_asset(test_app, asset_create1)
    message = await checked_request(
        test_app.post("/assets/", json=asset_create1.dict()), Message, 409
    )
    assert "asyncpg.exceptions.UniqueViolationError" in message.message
    assert str(asset_create1.short_name) in message.message


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset"])
async def test_get_asset(test_app: AsyncClient, asset_create1: AssetCreate) -> None:
    response = await create_asset(test_app, asset_create1)
    asset_id = response.id
    assert asset_id is not None
    asset = await checked_request(test_app.get(f"/assets/{asset_id}"), Asset)
    assert asset.name == asset_create1.name
    assert asset.short_name == asset_create1.short_name
    assert asset.type == asset_create1.type


@pytest.mark.asyncio
async def test_get_asset_not_found(test_app: AsyncClient) -> None:
    asset_id = str(uuid.uuid4())
    message = await checked_request(test_app.get(f"/assets/{asset_id}"), Message, 404)
    assert message.message == "Asset not found"


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset"])
async def test_get_assets(
    test_app: AsyncClient, asset_create_list2: list[AssetCreate]
) -> None:
    asset1 = asset_create_list2[0]
    asset2 = asset_create_list2[1]
    await create_asset(test_app, asset1)
    await create_asset(test_app, asset2)
    items = await checked_page_elements(test_app.get("/assets/"), Asset)
    assert len(items) == 2
    short_names = {item.short_name for item in items}
    assert {asset1.short_name, asset2.short_name} == short_names


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset"])
async def test_get_assets_with_filter(
    test_app: AsyncClient, asset_create_list2: list[AssetCreate]
) -> None:
    asset1 = asset_create_list2[0]
    asset2 = asset_create_list2[1]
    await create_asset(test_app, asset1)
    await create_asset(test_app, asset2)
    items = await checked_page_elements(
        test_app.get(f"/assets/", params={"short_name": asset2.short_name}), Asset
    )
    assert len(items) == 1
    short_names = {item.short_name for item in items}
    assert {asset2.short_name} == short_names


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset"])
async def test_delete_asset(test_app: AsyncClient, asset_create1: AssetCreate) -> None:
    asset = await create_asset(test_app, asset_create1)
    asset_id = asset.id
    assert asset_id is not None

    response = await test_app.delete(f"/assets/{asset_id}")
    assert response.status_code == 204
    message = await checked_request(test_app.get(f"/assets/{asset_id}"), Message, 404)
    assert message.message == "Asset not found"


@pytest.mark.asyncio
async def test_delete_asset_not_found(test_app: AsyncClient) -> None:
    asset_id = str(uuid.uuid4())

    message = await checked_request(
        test_app.delete(f"/assets/{asset_id}"), Message, 404
    )
    assert message.message == "Asset not found"


async def create_asset_pair(
    test_app: AsyncClient, asset_pair_create: AssetPairCreate
) -> AssetPair:
    return await checked_request(
        test_app.post("/assets/pairs/", json=schema_to_json_payload(asset_pair_create)),
        AssetPair,
    )


@pytest.mark.asyncio
@pytest.mark.dependency(name="create_asset_pair")
async def test_create_asset_pair(
    test_app: AsyncClient, asset_pair_create1: AssetPairCreate
) -> None:
    asset_pair = await create_asset_pair(test_app, asset_pair_create1)
    assert asset_pair.base_id == asset_pair_create1.base_id
    assert asset_pair.quote_id == asset_pair_create1.quote_id


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset_pair"])
async def test_get_asset_pair(
    test_app: AsyncClient, asset_pair_create1: AssetPairCreate
) -> None:
    response = await create_asset_pair(test_app, asset_pair_create1)
    asset_pair_id = response.id
    assert asset_pair_id is not None
    asset_pair = await checked_request(
        test_app.get(f"/assets/pairs/{asset_pair_id}"), AssetPair
    )
    assert asset_pair.base_id == asset_pair_create1.base_id
    assert asset_pair.quote_id == asset_pair_create1.quote_id


@pytest.mark.asyncio
async def test_get_asset_pair_not_found(test_app: AsyncClient) -> None:
    asset_pair_id = str(uuid.uuid4())
    message = await checked_request(
        test_app.get(f"/assets/pairs/{asset_pair_id}"), Message, 404
    )
    assert message.message == "Asset pair not found"


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset_pair"])
async def test_get_asset_pairs(
    test_app: AsyncClient, asset_pair_create_list2: list[AssetPairCreate]
) -> None:
    asset_pair1 = asset_pair_create_list2[0]
    asset_pair2 = asset_pair_create_list2[1]
    await create_asset_pair(test_app, asset_pair1)
    await create_asset_pair(test_app, asset_pair2)
    items = await checked_page_elements(test_app.get("/assets/pairs/"), AssetPair)
    assert len(items) == 2
    base_ids = {item.base_id for item in items}
    assert {asset_pair1.base_id, asset_pair2.base_id} == base_ids


@pytest.mark.asyncio
@pytest.mark.dependency(depends=["create_asset_pair"])
async def test_delete_asset_pair(
    test_app: AsyncClient, asset_pair_create1: AssetPairCreate
) -> None:
    asset_pair = await create_asset_pair(test_app, asset_pair_create1)
    asset_pair_id = asset_pair.id
    assert asset_pair_id is not None

    response = await test_app.delete(f"/assets/pairs/{asset_pair_id}")
    assert response.status_code == 204
    message = await checked_request(
        test_app.get(f"/assets/pairs/{asset_pair_id}"), Message, 404
    )
    assert message.message == "Asset pair not found"


@pytest.mark.asyncio
async def test_delete_asset_pair_not_found(test_app: AsyncClient) -> None:
    asset_pair_id = str(uuid.uuid4())

    message = await checked_request(
        test_app.delete(f"/assets/pairs/{asset_pair_id}"), Message, 404
    )
    assert message.message == "Asset pair not found"
