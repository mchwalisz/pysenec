import aiohttp

from .constants import SYSTEM_STATE_NAME
from .util import parse


class Senec:
    """Senec Home Battery Sensor

    """

    def __init__(self, host, websession):
        self.host = host
        self.websession: aiohttp.websession = websession

    async def update(self):
        url = f"http://{self.host}/lala.cgi"
        json = {"ENERGY": {"STAT_STATE": ""}}

        async with self.websession.post(url, json=json) as res:
            res.raise_for_status()
            data = await res.json()
            self.stat_state = SYSTEM_STATE_NAME[parse(data["ENERGY"]["STAT_STATE"])]
            return self.stat_state
