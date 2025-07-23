import asyncio
import random
import string
from flask import (
    render_template, request, redirect, flash
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

    if form.validate_on_submit():
        original_link = form.original_link.data
        custom_id = form.custom_id.data
        if not custom_id or not custom_id.strip():
            custom_id = get_unique_short_id()
        else:
            custom_id = custom_id.strip()
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
        short_url = f"{request.host_url.rstrip('/')}/{custom_id}"
        return render_template('index.html', form=form, short_url=short_url)
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def file_upload_view():
    form = FileUploadForm()
    uploaded = []

    if request.method == 'POST':
        files = request.files.getlist('files')
        valid_files = [f for f in files if f.filename and f.filename.strip()]
        if not valid_files:
            flash('Нет файлов для загрузки', 'danger')
            return render_template('files.html', form=form)
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, async_upload_files_to_yadisk(
                                valid_files))
                        public_urls = future.result()
                else:
                    public_urls = loop.run_until_complete(
                        async_upload_files_to_yadisk(valid_files))
            except RuntimeError:
                public_urls = asyncio.run(
                    async_upload_files_to_yadisk(valid_files)
                )
        except Exception as e:
            flash(f'Ошибка загрузки файлов: {e}', 'danger')
            return render_template('files.html', form=form)
        for file, public_url in zip(valid_files, public_urls):
            if public_url:
                filename = secure_filename(file.filename)
                short_id = get_unique_short_id()
                file_record = FileMap(
                    filename=filename,
                    short=short_id,
                    original_url=public_url
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
        return redirect(file_link.original_url)
    return render_template('errors/404.html'), 404