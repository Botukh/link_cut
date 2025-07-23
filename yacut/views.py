import os
import asyncio

from flask import (
    render_template, request, redirect, flash, url_for
)
from werkzeug.utils import secure_filename

from . import main_bp
from .forms import URLForm, FileUploadForm
from .models import db, URLMap, FileMap
from .utils import get_unique_short_id
from .ydisk import upload_file_to_disk, publish_and_get_public_url


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
        files = form.files.data
        if not files:
            flash('Файлы не выбраны', 'danger')
            return render_template('files.html', form=form, uploaded=uploaded)

        async def process_files():
            uploaded_local = []
            for file in files:
                filename = secure_filename(file.filename)
                ydisk_path = f'disk:/yacut/{filename}'
                file_data = file.read()

                await upload_file_to_disk(file_data, ydisk_path)
                public_url = await publish_and_get_public_url(ydisk_path)

                short_id = get_unique_short_id()
                file_entry = FileMap(
                    filename=filename, ydisk_path=ydisk_path, short=short_id)
                db.session.add(file_entry)
                uploaded_local.append((filename, short_id, public_url))

            db.session.commit()
            return uploaded_local

        uploaded_files = asyncio.run(process_files())

        if uploaded_files:
            flash('Файлы успешно загружены', 'success')
            return render_template(
                'files.html', form=form, uploaded=uploaded_files)

    return render_template('files.html', form=form, uploaded=uploaded)


@main_bp.route('/<string:short>')
def redirect_view(short):
    link = URLMap.query.filter_by(short=short).first()
    if link:
        return redirect(link.original)

    file_link = FileMap.query.filter_by(short=short).first()
    if file_link:
        return redirect(file_link.ydisk_path)

    flash('Ссылка не найдена.', 'danger')
    return redirect(url_for('main_bp.index_view'))
