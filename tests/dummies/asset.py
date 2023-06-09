from random import seed

from backend.api.schemas import AssetCreate
from tests.random_seed import test_seed
from tests.utils import rand_str

seed(test_seed)


# TODO: Move to fixture? Use in fixtures?
def random_asset_create() -> AssetCreate:
    return AssetCreate(name=rand_str(), short_name=rand_str(), type=rand_str())
