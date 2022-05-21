from functools import partial

import pytest
from aiohttp.client import ClientSession

import pysenec


def pytest_addoption(parser):
    parser.addoption(
        "--senec-host",
        type=str,
        action="store",
        help="Local Senec host (or IP)",
        default="senec.local",
    )


def before_record_cb(request, host):
    """Filters requests"""
    request.uri = request.uri.replace(host, "senec_device_redacted")
    return request


@pytest.fixture(scope="module")
def vcr_config(request):
    host = request.config.getoption("--senec-host")
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        "filter_headers": [("authorization", "DUMMY")],
        "before_record_request": partial(before_record_cb, host=host),
    }


@pytest.fixture
def create_session(event_loop):
    session = None

    async def maker(*args, **kwargs):
        nonlocal session
        session = ClientSession(*args, **kwargs)
        return session

    yield maker
    if session is not None:
        event_loop.run_until_complete(session.close())


@pytest.fixture()
async def senec(request, create_session):
    host = request.config.getoption("--senec-host")
    session = await create_session()
    senec = pysenec.Senec(host, session)
    return senec
