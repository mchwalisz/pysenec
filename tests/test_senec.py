import pytest

import pysenec


async def test_basic(senec):
    assert isinstance(senec, pysenec.Senec)


@pytest.mark.vcr()
async def test_update(senec):
    await senec.update()
