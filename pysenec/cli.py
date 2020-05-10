import argparse
import asyncio
from pprint import pprint

import aiohttp
import pysenec


async def run(host, verbose=False):
    async with aiohttp.ClientSession() as session:
        senec = pysenec.Senec(host, session)
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
