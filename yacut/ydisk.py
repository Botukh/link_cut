import aiohttp
import os


DISK_TOKEN = os.getenv('DISK_TOKEN')
BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


async def upload_file_to_disk(file_data, ydisk_path):

    upload_url = f"{BASE_URL}/upload"
    params = {'path': ydisk_path, 'overwrite': 'true'}

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.get(upload_url, params=params) as resp:
            if resp.status != 200:
                raise Exception(
                    f"Ошибка получения upload_url: {await resp.text()}")
            upload_link = (await resp.json())['href']

        async with session.put(upload_link, data=file_data) as upload_resp:
            if upload_resp.status not in (200, 201):
                raise Exception(f"Ошибка загрузки: {await upload_resp.text()}")


async def publish_and_get_public_url(ydisk_path):

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        params = {'path': ydisk_path}
        publish_url = f"{BASE_URL}/publish"

        async with session.put(publish_url, params=params) as pub_resp:
            if pub_resp.status not in (200, 201, 409):
                raise Exception(f"Ошибка публикации: {await pub_resp.text()}")

        async with session.get(BASE_URL, params=params) as info_resp:
            if info_resp.status != 200:
                raise Exception(
                    f"Ошибка получения info: {await info_resp.text()}")
            return (await info_resp.json()).get('public_url')
