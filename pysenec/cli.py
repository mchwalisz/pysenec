import argparse
import asyncio

import aiohttp
import pysenec


async def run(host):
    async with aiohttp.ClientSession() as session:
        senec = pysenec.Senec(host, session)
        data = await senec.update()
        print(data)


def main():
    parser = argparse.ArgumentParser(description="Senec Home Battery Sensor")
    parser.add_argument("--host", help="Local Senec host (or IP)")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(args.host))


if __name__ == "__main__":
    main()
