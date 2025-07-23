import asyncio
import random
import string
from flask import (
    render_template, request, redirect, flash, url_for
)
from werkzeug.utils import secure_filename

from . import app, db
from .forms import URLMapForm, FileUploadForm
from .models import URLMap, FileMap
from .ydisk import async_upload_files_to_yadisk


CHARS = string.ascii_letters + string.digits


def get_unique_short_id(length=6):
    while True:
        short_id = ''.join(random.choices(CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first() and \
           not FileMap.query.filter_by(short=short_id).first():
            return short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    short_id = None

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = (
            form.custom_id.data or '').strip() or get_unique_short_id()

        if custom_id.lower() == 'files':
            flash(
                'Предложенный вариант короткой ссылки уже существует.',
                'danger')
            return render_template('index.html', form=form)

        existing = URLMap.query.filter_by(short=custom_id).first()
        if existing:
            flash(
                'Предложенный вариант короткой ссылки уже существует.',
                'danger')
            return render_template('index.html', form=form)

        new_link = URLMap(original=original_link, short=custom_id)
        db.session.add(new_link)
        db.session.commit()

        short_id = request.host_url + custom_id
        flash(
            f'Ссылка создана: <a href="{short_id}">{short_id}</a>', 'success')

    return render_template('index.html', form=form, short_id=short_id)


@app.route('/files', methods=['GET', 'POST'])
def file_upload_view():
    form = FileUploadForm()
    uploaded = []

    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files or not any(f.filename for f in files):
            flash('Нет файлов для загрузки', 'danger')
            return redirect(request.url)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            public_urls = loop.run_until_complete(
                async_upload_files_to_yadisk(files))
        except Exception as e:
            flash(f'Ошибка загрузки файлов: {e}', 'danger')
            return redirect(request.url)

        for file, public_url in zip(files, public_urls):
            filename = secure_filename(file.filename)
            short_id = get_unique_short_id()

            file_record = FileMap(
                filename=filename,
                short=short_id,
                ydisk_path=public_url
            )
            db.session.add(file_record)
            uploaded.append((filename, short_id, public_url))

        db.session.commit()

        return render_template('files.html', form=form, uploaded=uploaded)

    return render_template('files.html', form=form)


@app.route('/<string:short>')
def redirect_view(short):
    link = URLMap.query.filter_by(short=short).first()
    if link:
        return redirect(link.original)

    file_link = FileMap.query.filter_by(short=short).first()
    if file_link:
        return redirect(file_link.ydisk_path)

    flash('Ссылка не найдена.', 'danger')
    return redirect(url_for('index_view'))
