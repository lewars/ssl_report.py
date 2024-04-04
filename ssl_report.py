#!/usr/bin/env python3

"""
A simple script to retrieve SSL scan reports using the SSL Labs API asynchronously and generates a report.

Usage:
  ssl_report.py <host1> <host2> ... <hostN>
"""

import os
import asyncio
import aiohttp
from typing import Union, Dict
from rich.console import Console
console = Console()

WAIT_TIME = 30
API_URL = "https://api.ssllabs.com/api/v2/"
# get environment variable for debug mode
DEBUG = os.getenv("DEBUG", False)

async def check_host_evaluation_status(session: aiohttp.ClientSession, host: str) -> bool:
    """ Check the evaluation status of the host.

      Args:
          session (aiohttp.ClientSession): The aiohttp session object.
          host (str): The host to check the evaluation status for.
      Returns:
          bool: True if the evaluation is in progress, False otherwise.
      """
    async with session.get(f"{API_URL}/analyze", params={"host": host, "all": "done", "fromCache": "off"}) as response:
        if response.status == 200:
            data = await response.json()
            if DEBUG:
                print(data)
            if data['status'] == 'PROGRESS':
                return True
    return False

async def get_ssl_data(session: aiohttp.ClientSession, host: str) -> Union[Dict, None]:
    """ Get SSL data for the host.

      Args:
          session (aiohttp.ClientSession): The aiohttp session object.
          host (str): The host to get SSL data for.
      Returns:
          Union[Dict, None]: The SSL data if available, None otherwise.
      """

    start_new = "on"
    all_data = "done"
    from_cache = "off"

    if not await check_host_evaluation_status(session, host):
        async with session.get(f"{API_URL}analyze",
                               params={"host": host, "startNew": start_new, "all": all_data, "fromCache": from_cache}) as response:
            if DEBUG:
                print(response)
            if response.status != 200:
                return {"status": "ERROR", "errors": [{"message": f"Failed to initiate SSL scan for {host}."}]}

    while True:
        async with session.get(f"{API_URL}analyze",
                               params={"host": host, "all": all_data, "fromCache": from_cache, "maxAge": 1 }) as status_response:
            if status_response.status != 200:
                return {"status": "ERROR", "errors": [{"message": f"Failed to initiate SSL scan for {host}."}]}
            data = await status_response.json()
            if DEBUG:
                print(data)
            if data["status"] in ["READY", "ERROR"]:
                break
        await asyncio.sleep(WAIT_TIME)

    return data

def gen_report(status_data: dict, host: str) -> str:
    report = f"SSL Scan Report for {host}\n\n"
    if status_data["status"] == "ERROR":
        return "Scan could not be completed due to an error.\n"

    for endpoint in status_data.get("endpoints", []):
        report += f"IP Address: {endpoint.get('ipAddress')}\n"
        report += f"Server Name: {endpoint.get('serverName')}\n"
        report += f"Grade: {endpoint.get('grade')}\n"
        report += f"Status Message: {endpoint.get('statusMessage')}\n"
        report += "-" * 40 + "\n"

    return report

async def main(hosts):
    async with aiohttp.ClientSession() as session:
        for host in hosts:
            ssl_data = await get_ssl_data(session, host)
            if not ssl_data or ssl_data["status"] == "ERROR":
                print(f"Failed to retrieve SSL data for {host}.")
                if ssl_data["status"] == "ERROR":
                    # parse error : {"errors":[{"field":"host","message":"qp.mandatory"}]}
                    for err in ssl_data["errors"]:
                        print(f"Host: {host} Error: {err['message']}")
                continue
            report_text = gen_report(ssl_data, host)
            print(report_text)

if __name__ == "__main__":
    import sys

    hosts = sys.argv[1:]
    if len(hosts) < 1:
        print("Usage: ssl_report.py <host1> <host2> ... <hostN>")
        sys.exit(1)

    with console.status("[bold]Analyzing hosts SSL...", spinner="dots"):
        asyncio.run(main(hosts))
