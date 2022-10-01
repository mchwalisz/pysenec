import aiohttp

from .constants import SYSTEM_STATE_NAME, SYSTEM_TYPE_NAME
from .util import parse


class Senec:
    """Senec Home Battery Sensor"""
    
    def __init__(self, host, websession):
        self.host = host
        self.websession: aiohttp.websession = websession
        self.url = f"http://{host}/lala.cgi"

        self.type=None #variables for late config
        self.hasWallbox=False
        self.defaultForm=None
        self.allForm=None

        self._ident=None
        self._raw=None

    @property
    def system_type(self) -> str:
        """
        type name of the senec system
        """
        
        return SYSTEM_TYPE_NAME.get(self.type,"UNKNOWN")
        
    @property
    def system_state(self) -> str:
        """
        Textual descritpion of energy status

        """
        value = self._raw["ENERGY"]["STAT_STATE"]
        return SYSTEM_STATE_NAME.get(value, "UNKNOWN")

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
        """
        value = self._raw["WALLBOX"]["APPARENT_CHARGING_POWER"][0]
        if value >0:
            return value
        return 0

    @property
    def wallbox_imported_power(self) -> float:
        """
        Wallbox Total Discharging Power (W) - currently not useable but needed as dummy for energy dashboard
        """
        value = self._raw["WALLBOX"]["APPARENT_CHARGING_POWER"][0]
        if value <0:
            return abs(value)
        return 0

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

    @property
    def battery_temp(self) -> float:
        """
        Current battery temperature

        """
        return self._raw["TEMPMEASURE"]["BATTERY_TEMP"]

    @property
    def case_temp(self) -> float:
        """
        Current case temperature

        """
        return self._raw["TEMPMEASURE"]["CASE_TEMP"]

    @property
    def mcu_temp(self) -> float:
        """
        Current controller temperature

        """
        return self._raw["TEMPMEASURE"]["MCU_TEMP"]

    async def late_config(self):

        identForm = {
            "FACTORY": {
                "SYS_TYPE": "",
                "PM_TYPE": "",
                "CELL_TYPE": "",
                "BAT_TYPE": "",
            },
            "FEATURES": { "CAR" : "", },
            "PM1OBJ1": { "ENABLED": "",  },
            "PM1OBJ2": { "ENABLED": "",  },
            "PM1OBJ3": { "ENABLED": "",  },
            "PV1" :  { "INTERNAL_MD_MODEL": "", },
            "WALLBOX" :  { "HW_TYPE":  "" , },
        }
        
        async with self.websession.post(self.url, json=identForm) as res:
            res.raise_for_status()
            self._ident = parse(await res.json())

        # now create forms for the different versions
        
        self.defaultForm = {
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
                "LIVE_WB_ENERGY": "",
            },
            "TEMPMEASURE": {
                "BATTERY_TEMP": "",
                "CASE_TEMP": "",
                "MCU_TEMP": "",
            },
            "PV1": {"POWER_RATIO": ""},
            "PWR_UNIT": {"POWER_L1": "", "POWER_L2": "", "POWER_L3": ""},
        }
    
        self.allForm = {
            "STATISTIC": {},
            "ENERGY": {},
            "FEATURES": {},
            "LOG": {},
            "SYS_UPDATE": {},
            "WIZARD": {},
            "BMS": {},
            "BAT1": {},
            "PWR_UNIT": {},
            "PV1": {},
        }

        #print(self._ident)
        
        # now modify according to version info
        try:
            if self._ident["FACTORY"]["SYS_TYPE"] == 18:
                
                # try to use same version from SYS_TYPE,
                # maybe we have to switch to something self defined. 
                self.type=18
                
                if self._ident["WALLBOX"]["HW_TYPE"][0] >0:
                    self.hasWallbox=True
                    
                self.allForm.update({ "BAT1OBJ1": {},})
                    
                    
            if self._ident["PM1OBJ1"]["ENABLED"] == 1:
                self.defaultForm.update({
                    "PM1OBJ1": {"FREQ": "", "U_AC": "", "I_AC": "", "P_AC": "", "P_TOTAL": ""},
                })
                self.allForm.update( { "PM1OBJ1": {} , } )
            
            if self._ident["PM1OBJ2"]["ENABLED"] == 1:
                self.defaultForm.update( {
                    "PM1OBJ2": {"FREQ": "", "U_AC": "", "I_AC": "", "P_AC": "", "P_TOTAL": ""},
                })
                self.allForm.update( { "PM1OBJ2": {} , } )

        except (KeyError, ValueError) as e:
            #maybe we should use logging to put a warning here...
            print ("error on late_config "+str(e))
            pass
        
        if self.hasWallbox:
            self.defaultForm.update( {
                "WALLBOX": {"APPARENT_CHARGING_POWER": "",
                            "L1_CHARGING_CURRENT": "",
                            "L2_CHARGING_CURRENT": "",
                            "L3_CHARGING_CURRENT": "",
                            "EV_CONNECTED": ""},
            })
            self.allForm.update( {
                            "WALLBOX": {},
            })
        

    async def update(self):
        if not self.type:
            await self.late_config()
        await self.read_senec(self.defaultForm)

    async def read_senec(self, form):
        """Read values used by webinterface from Senec Home v2.1

        Note: Not all values are "high priority" and reading everything causes problems with Senec device, i.e. no sync with Senec cloud possible.
        """

        async with self.websession.post(self.url, json=form) as res:
            res.raise_for_status()
            self._raw = parse(await res.json())
