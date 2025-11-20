import asyncio
import os
from json import JSONDecodeError
import dotenv
from yarl import URL

import crawler
from crawler import Crawler, Server
from crawler.crawler import NotHTMLPageError
from crawler.url_manager import JsonURLManager

crawler.utils.setup_logging()
dotenv.load_dotenv()

source_store_path = os.getenv('SOURCE_STORE_PATH')
root_url = os.getenv('ROOT_URL')
data_file_path = os.getenv('DATA_FILE_PATH')

os.makedirs(source_store_path, exist_ok=True)
url_manager = JsonURLManager(data_file_path)

try:
    asyncio.run(url_manager.load())
except (JSONDecodeError, FileNotFoundError):
    asyncio.run(url_manager.save())

crawler_instance = Crawler(
    root_url,
    source_store_path,
    url_manager
)
server = Server(
    root_url,
    source_store_path,
    url_manager
)
server.setup()

async def not_found_handler(url: URL):
    try:
        await crawler_instance.download_page(url)
    except NotHTMLPageError:
        await crawler_instance.download_single_url(url)
server.not_found_handler = not_found_handler


async def main():
    async with crawler_instance:
        await server.run()

asyncio.run(main())