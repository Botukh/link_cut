import asyncio
import aiohttp
from urllib.parse import quote

from . import app

API_HOST = 'https://cloud-api.yandex.net'
API_VERSION = '/v1'
DISK_TOKEN = app.config['DISK_TOKEN']
AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


async def async_upload_files_to_yadisk(files):
    if not files:
        return []
    tasks = []
    async with aiohttp.ClientSession() as session:
        for file in files:
            tasks.append(
                asyncio.ensure_future(
                    upload_file_and_get_public_url(session, file)
                )
            )
        return await asyncio.gather(*tasks)


async def upload_file_and_get_public_url(session, file):
    filename = quote(file.filename)
    upload_url = f'{API_HOST}{API_VERSION}/disk/resources/upload'
    params = {'path': f'app:/{filename}', 'overwrite': 'true'}

    async with session.get(
        upload_url,
        headers=AUTH_HEADERS,
        params=params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        href = data['href']

    async with session.put(href, data=file.read()) as resp:
        resp.raise_for_status()

    publish_url = f'{API_HOST}{API_VERSION}/disk/resources/publish'
    publish_params = {'path': f'app:/{filename}'}

    async with session.put(
        publish_url,
        headers=AUTH_HEADERS,
        params=publish_params
    ) as resp:
        resp.raise_for_status()

    meta_url = f'{API_HOST}{API_VERSION}/disk/resources'
    async with session.get(
        meta_url,
        headers=AUTH_HEADERS,
        params=publish_params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get('public_url')
