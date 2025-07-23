import os
import aiohttp
import asyncio

from flask import (
    Blueprint, render_template, request, redirect, flash, url_for
)
from werkzeug.utils import secure_filename
from urllib.parse import quote

from . import main_bp
from .forms import URLForm, FileUploadForm
from .models import db, URLMap, FileMap
from .utils import get_unique_short_id


DISK_TOKEN = os.getenv('DISK_TOKEN')
API_HOST = 'https://cloud-api.yandex.net'
API_VERSION = 'v1/disk'
UPLOAD_ENDPOINT = f'{API_HOST}/{API_VERSION}/resources/upload'
PUBLISH_ENDPOINT = f'{API_HOST}/{API_VERSION}/resources/publish'
METADATA_ENDPOINT = f'{API_HOST}/{API_VERSION}/resources'


@main_bp.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    short_url = None

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data.strip() or get_unique_short_id()

        if custom_id.lower() == 'files':
            flash(
                'Предложенный вариант короткой ссылки уже существует.',
                'danger'
            )
            return render_template('index.html', form=form)

        existing = URLMap.query.filter_by(short=custom_id).first()
        if existing:
            flash(
                'Предложенный вариант короткой ссылки уже существует.',
                'danger'
            )
            return render_template('index.html', form=form)

        new_link = URLMap(original=original_link, short=custom_id)
        db.session.add(new_link)
        db.session.commit()

        short_url = request.host_url + custom_id
        flash(
            f'Ссылка создана: <a href="{short_url}">{short_url}</a>',
            'success'
        )

    return render_template('index.html', form=form, short_url=short_url)


@main_bp.route('/files', methods=['GET', 'POST'])
def file_upload_view():
    form = FileUploadForm()
    uploaded = FileMap.query.order_by(FileMap.id.desc()).all()

    if request.method == 'POST' and form.validate_on_submit():
        uploaded_file = form.file.data
        if not uploaded_file:
            flash('Файл не выбран', 'danger')
            return render_template('files.html', form=form, uploaded=uploaded)

        filename = secure_filename(uploaded_file.filename)
        if not filename:
            flash('Некорректное имя файла.', 'danger')
            return render_template('files.html', form=form, uploaded=uploaded)

        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, filename)
        uploaded_file.save(tmp_path)
        disk_path = f'disk:/yacut/{filename}'

        headers = {
            'Authorization': f'OAuth {DISK_TOKEN}',
            'Content-Type': 'application/json'
        }

        async def upload_file():
            async with aiohttp.ClientSession() as session:
                params = {'path': disk_path, 'overwrite': 'true'}
                async with session.get(UPLOAD_ENDPOINT, headers=headers, params=params) as resp:
                    if resp.status != 200:
                        flash('Не удалось получить ссылку для загрузки.', 'danger')
                        return None
                    upload_info = await resp.json()
                    href = upload_info.get('href')
                    if not href:
                        flash('Ошибка: отсутствует upload URL.', 'danger')
                        return None

                with open(tmp_path, 'rb') as f:
                    async with session.put(href, data=f) as put_resp:
                        if put_resp.status not in (201, 202):
                            flash('Ошибка загрузки файла на Яндекс.Диск.', 'danger')
                            return None

                publish_url = f'{PUBLISH_ENDPOINT}?path={quote(disk_path)}'
                await session.put(publish_url, headers=headers)

                meta_url = f'{METADATA_ENDPOINT}?path={quote(disk_path)}'
                async with session.get(meta_url, headers=headers) as meta_resp:
                    if meta_resp.status != 200:
                        flash('Не удалось получить метаданные файла.', 'warning')
                        return None
                    meta_data = await meta_resp.json()
                    return meta_data.get('public_url', disk_path)

        public_url = asyncio.run(upload_file())
        if not public_url:
            return render_template('files.html', form=form, uploaded=uploaded)

        short_id = get_unique_short_id(FileMap)
        file_entry = FileMap(
            filename=filename,
            short=short_id,
            path=public_url
        )
        db.session.add(file_entry)
        db.session.commit()

        flash('Файл успешно загружен!', 'success')
        return redirect(url_for('main.file_upload_view'))

    return render_template('files.html', form=form, uploaded=uploaded)


@main_bp.route('/<string:short>')
def follow_short_link(short):
    urlmap = URLMap.query.filter_by(short=short).first()
    if urlmap:
        return redirect(urlmap.original)
    filemap = FileMap.query.filter_by(short=short).first()
    if filemap:
        return redirect(filemap.path)
    flash('Ссылка не найдена.', 'danger')
    return redirect(url_for('main.index_view'))
