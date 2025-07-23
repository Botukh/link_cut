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
    results = []
    async with aiohttp.ClientSession() as session:
        for file in files:
            try:
                public_url = await upload_file_and_get_public_url(
                    session, file)
                results.append(public_url)
            except Exception as e:
                print(f"Error uploading file {file.filename}: {e}")
                results.append(None)
    return results


async def upload_file_and_get_public_url(session, file):
    file.seek(0)
    file_data = file.read()
    file.seek(0)
    filename = quote(file.filename)
    file_path = f'app:/{filename}'
    upload_url = f'{API_HOST}{API_VERSION}/disk/resources/upload'
    params = {'path': file_path, 'overwrite': 'true'}

    async with session.get(
        upload_url,
        headers=AUTH_HEADERS,
        params=params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        href = data['href']
    async with session.put(href, data=file_data) as resp:
        resp.raise_for_status()
    download_url = f'{API_HOST}{API_VERSION}/disk/resources/download'
    download_params = {'path': file_path}
    async with session.get(
        download_url,
        headers=AUTH_HEADERS,
        params=download_params
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get('href')