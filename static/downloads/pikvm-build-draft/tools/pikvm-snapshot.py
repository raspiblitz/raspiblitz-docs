#!/usr/bin/env python3
"""Capture one PiKVM frame over its local, authenticated Unix socket.

Run on the PiKVM as root. A short-lived WebSocket starts the video streamer
even when nobody has the web interface open. Credentials stay on the PiKVM.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

import aiohttp


def read_headers(path: Path) -> dict[str, str]:
    headers = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("header = "):
            continue
        name, value = json.loads(line.split("=", 1)[1].strip()).split(": ", 1)
        headers[name] = value
    if not {"X-KVMD-User", "X-KVMD-Passwd"}.issubset(headers):
        raise ValueError("PiKVM API credentials are incomplete")
    return headers


async def capture(output: Path, config: Path) -> None:
    connector = aiohttp.UnixConnector(path="/run/kvmd/kvmd.sock")
    async with aiohttp.ClientSession(
        connector=connector, headers=read_headers(config)
    ) as session:
        async with session.ws_connect("http://localhost/ws?stream=1", heartbeat=10):
            clock = asyncio.get_running_loop().time
            deadline = clock() + 30
            # uStreamer can initially serve its old NO SIGNAL placeholder while
            # the capture device is starting. Prefer a live frame when available,
            # but still return a diagnostic placeholder if no signal appears.
            offline_deadline = clock() + 8
            while clock() < deadline:
                try:
                    stream = aiohttp.UnixConnector(path="/run/kvmd/ustreamer.sock")
                    async with aiohttp.ClientSession(
                        connector=stream, timeout=aiohttp.ClientTimeout(total=5)
                    ) as direct:
                        async with direct.get("http://localhost/snapshot") as response:
                            if response.status == 200 and response.content_type == "image/jpeg":
                                data = await response.read()
                                if not data.startswith(b"\xff\xd8"):
                                    raise ValueError("PiKVM returned an invalid JPEG")
                                online = response.headers.get("X-UStreamer-Online", "true")
                                if online.lower() != "false" or clock() >= offline_deadline:
                                    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                                    with os.fdopen(fd, "wb") as image:
                                        image.write(data)
                                    return
                except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
                    pass
                await asyncio.sleep(0.5)
    raise RuntimeError("PiKVM did not provide a snapshot within 30 seconds")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new JPEG file on the PiKVM")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("/root/.config/raspiblitz-agent/kvmd-curl.conf"),
    )
    args = parser.parse_args()
    asyncio.run(capture(args.output, args.config))


if __name__ == "__main__":
    main()
