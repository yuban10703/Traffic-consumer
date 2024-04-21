import asyncio
import httpx
import json
from pathlib import Path
import sys

total_bytes_downloaded = 0

curFileDir = Path(sys.argv[0]).parent  # 当前文件路径

try:
    with open(curFileDir / "config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except:
    print("载入配置文件出错")
    exit(0)


async def download_file(client, url):
    global total_bytes_downloaded
    async with client.stream("GET", url) as response:
        old = 0
        async for _ in response.aiter_raw():
            # print(response.num_bytes_downloaded)
            download_size = response.num_bytes_downloaded - old
            # print(download_size)
            total_bytes_downloaded += download_size
            old = response.num_bytes_downloaded


async def main():
    global total_bytes_downloaded
    url = config["url"]
    max_concurrency = config["threads"]
    refresh_time = config["refresh_time"]
    async with httpx.AsyncClient(headers={},
                                 limits=httpx.Limits(max_keepalive_connections=None, max_connections=None,
                                                     keepalive_expiry=None)) as client:
        while True:
            tasks = len(asyncio.all_tasks()) - 1
            print(f"当前任务数: {tasks}")
            if tasks < max_concurrency:
                print("*" * 50)
                asyncio.create_task(download_file(client, url))
            print('\n' * 100)
            print(
                f"速度:{(total_bytes_downloaded) / (refresh_time * 1000000):.2f}MB/s 带宽: {(total_bytes_downloaded * 8) / (refresh_time * 1000000):.2f} Mbps")
            total_bytes_downloaded = 0
            await asyncio.sleep(refresh_time)


if __name__ == "__main__":
    asyncio.run(main())
