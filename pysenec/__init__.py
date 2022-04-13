import aiohttp

from .constants import SYSTEM_STATE_NAME
from .util import parse


class Senec:
    """Senec Home Battery Sensor"""

    def __init__(self, host, websession):
        self.host = host
        self.websession: aiohttp.websession = websession
        self.url = f"http://{host}/lala.cgi"

    @property
    def system_state(self) -> str:
        """
        Textual descritpion of energy status

        """
        value = self._raw["ENERGY"]["STAT_STATE"]
        return SYSTEM_STATE_NAME[value]

    @property
    def raw_status(self) -> dict:
        """
        Raw dict with all information

        """
        return self._raw

    @property
    def house_power(self) -> float:
        """
        Current power consumption (W)

        """
        return self._raw["ENERGY"]["GUI_HOUSE_POW"]

    @property
    def house_total_consumption(self) -> float:
        """
        Total energy used by house (kWh)

        Does not include Wallbox.
        """
        return self._raw["STATISTIC"]["LIVE_HOUSE_CONS"]

    @property
    def solar_generated_power(self) -> float:
        """
        Current power generated by solar panels (W)

        """
        return abs(self._raw["ENERGY"]["GUI_INVERTER_POWER"])

    @property
    def solar_total_generated(self) -> float:
        """
        Total energy generated by solar panels (kWh)

        """
        return self._raw["STATISTIC"]["LIVE_PV_GEN"]

    @property
    def battery_charge_percent(self) -> float:
        """
        Current battery charge value (%)

        """
        return self._raw["ENERGY"]["GUI_BAT_DATA_FUEL_CHARGE"]

    @property
    def battery_charge_power(self) -> float:
        """
        Current battery charging power (W)

        """
        value = self._raw["ENERGY"]["GUI_BAT_DATA_POWER"]
        if value > 0:
            return value
        return 0

    @property
    def battery_discharge_power(self) -> float:
        """
        Current battery discharging power (W)

        """
        value = self._raw["ENERGY"]["GUI_BAT_DATA_POWER"]
        if value < 0:
            return abs(value)
        return 0

    @property
    def battery_state_power(self) -> float:
        """
        Battery charging power (W)

        Value is positive when battery is charging
        Value is negative when battery is discharging.
        """
        return self._raw["ENERGY"]["GUI_BAT_DATA_POWER"]

    @property
    def battery_total_charged(self) -> float:
        """
        Total energy charged to battery (kWh)

        """
        return self._raw["STATISTIC"]["LIVE_BAT_CHARGE"]

    @property
    def battery_total_discharged(self) -> float:
        """
        Total energy discharged from battery (kWh)

        """
        return self._raw["STATISTIC"]["LIVE_BAT_DISCHARGE"]

    @property
    def grid_imported_power(self) -> float:
        """
        Current power imported from grid (W)

        """
        value = self._raw["ENERGY"]["GUI_GRID_POW"]
        if value > 0:
            return value
        return 0

    @property
    def grid_exported_power(self) -> float:
        """
        Current power exported to grid (W)

        """
        value = self._raw["ENERGY"]["GUI_GRID_POW"]
        if value < 0:
            return abs(value)
        return 0

    @property
    def grid_state_power(self) -> float:
        """
        Grid exchange power (W)

        Value is positive when power is imported from grid.
        Value is negative when power is exported to grid.
        """
        return self._raw["ENERGY"]["GUI_GRID_POW"]

    @property
    def grid_total_export(self) -> float:
        """
        Total energy exported to grid export (kWh)

        """
        return self._raw["STATISTIC"]["LIVE_GRID_EXPORT"]

    @property
    def grid_total_import(self) -> float:
        """
        Total energy imported from grid (kWh)

        """
        return self._raw["STATISTIC"]["LIVE_GRID_IMPORT"]

    @property
    def wallbox_power(self) -> float:
        """
        Wallbox Total Charging Power (W)
        Derived from the 3 phase voltages multiplied with the phase currents from the wallbox

        """
        return self._raw["WALLBOX"]["L1_CHARGING_CURRENT"][0] * self._raw["PM1OBJ1"]["U_AC"][0] + self._raw["WALLBOX"]["L2_CHARGING_CURRENT"][0] * self._raw["PM1OBJ1"]["U_AC"][1] + self._raw["WALLBOX"]["L3_CHARGING_CURRENT"][0] * self._raw["PM1OBJ1"]["U_AC"][2]

    @property
    def wallbox_ev_connected(self) -> bool:
        """
        Wallbox EV Connected

        """
        return self._raw["WALLBOX"]["EV_CONNECTED"][0]

    @property
    def wallbox_energy(self) -> float:
        """
        Wallbox Total Energy

        """
        return self._raw["STATISTIC"]["LIVE_WB_ENERGY"][0] / 1000.0
    
    async def update(self):
        await self.read_senec_v21()

    async def read_senec_v21(self):
        """Read values used by webinterface from Senec Home v2.1

        Note: Not all values are "high priority" and reading everything causes problems with Senec device, i.e. no sync with Senec cloud possible.
        """
        form = {
            "ENERGY": {
                "STAT_STATE": "",
                "GUI_BAT_DATA_POWER": "",
                "GUI_INVERTER_POWER": "",
                "GUI_HOUSE_POW": "",
                "GUI_GRID_POW": "",
                "GUI_BAT_DATA_FUEL_CHARGE": "",
                "GUI_CHARGING_INFO": "",
                "GUI_BOOSTING_INFO": "",
                "GUI_BAT_DATA_POWER": "",
                "GUI_BAT_DATA_VOLTAGE": "",
                "GUI_BAT_DATA_CURRENT": "",
                "GUI_BAT_DATA_FUEL_CHARGE": "",
                "GUI_BAT_DATA_OA_CHARGING": "",
                "STAT_LIMITED_NET_SKEW": "",
            },
            "STATISTIC": {
                "LIVE_BAT_CHARGE": "",
                "LIVE_BAT_DISCHARGE": "",
                "LIVE_GRID_EXPORT": "",
                "LIVE_GRID_IMPORT": "",
                "LIVE_HOUSE_CONS": "",
                "LIVE_PV_GEN": "",
            },
            "PV1": {"POWER_RATIO": ""},
            "PWR_UNIT": {"POWER_L1": "", "POWER_L2": "", "POWER_L3": ""},
            "PM1OBJ1": {"FREQ": "", "U_AC": "", "I_AC": "", "P_AC": "", "P_TOTAL": ""},
            "PM1OBJ2": {"FREQ": "", "U_AC": "", "I_AC": "", "P_AC": "", "P_TOTAL": ""},
            "WALLBOX": {"L1_CHARGING_CURRENT": "", "L2_CHARGING_CURRENT": "", "L3_CHARGING_CURRENT": "", "EV_CONNECTED": ""},
        }

        async with self.websession.post(self.url, json=form) as res:
            res.raise_for_status()
            self._raw = parse(await res.json())

    async def read_senec_v21_all(self):
        """Read ALL values from Senec Home v2.1

        Note: This causes high demand on the SENEC machine so it shouldn't run too often. Adverse effects: No sync with Senec possible if called too often.
        """
        form = {
            "STATISTIC": {},
            "ENERGY": {},
            "FEATURES": {},
            "LOG": {},
            "SYS_UPDATE": {},
            "WIZARD": {},
            "BMS": {},
            "BAT1": {},
            "BAT1OBJ1": {},
            "BAT1OBJ2": {},
            "BAT1OBJ2": {},
            "BAT1OBJ3": {},
            "BAT1OBJ4": {},
            "PWR_UNIT": {},
            "PV1": {},
        }

        async with self.websession.post(self.url, json=form) as res:
            res.raise_for_status()
            self._raw = parse(await res.json())
