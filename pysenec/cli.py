import argparse
import asyncio
from pprint import pprint

import aiohttp

import pysenec


async def run(host, verbose=False):
    async with aiohttp.ClientSession() as session:
        senec = pysenec.Senec(host, session)
        if verbose:
            await senec.read_senec_v21_all()
        else:
            await senec.update()
        print(f"System state: {senec.system_state}")
        print(f"House energy use: {senec.house_power / 1000 :.3f} kW")
        print(f"Solar Panel generate: {senec.solar_generated_power / 1000 :.3f} kW")
        print(
            f"Battery: {senec.battery_charge_percent :.1f} % charge: {senec.battery_charge_power / 1000 :.3f} kW, discharge {senec.battery_discharge_power / 1000 :.3f} kW"
        )
        print(
            f"Grid: exported {senec.grid_exported_power / 1000 :.3f} kW, imported {senec.grid_imported_power / 1000 :.3f} kW"
        )
        print("")
        print(f"Total house use {senec.house_total_consumption :.3f} kWh")
        print(f"Total solar generation {senec.solar_total_generated :.3f} kWh")
        print(
            f"Total grid imported {senec.grid_total_import :.3f} kWh, export {senec.grid_total_export :.3f} kWh"
        )
        print(
            f"Total battery charged {senec.battery_total_charged :.3f} kWh, discharged {senec.grid_total_export :.3f} kWh"
        )
        if verbose:
            pprint(senec.raw_status)


def main():
    parser = argparse.ArgumentParser(description="Senec Home Battery Sensor")
    parser.add_argument("--host", help="Local Senec host (or IP)")
    parser.add_argument("--all", help="Prints extended info", action="store_true")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(args.host, verbose=args.all))


if __name__ == "__main__":
    main()
