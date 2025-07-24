import asyncio
import aiohttp
from http import HTTPStatus

from flask import render_template, request, redirect, flash, url_for

from . import app
from .forms import URLMapForm, FileUploadForm
from .models import URLMap
from .ydisk import async_upload_files_to_yadisk
from .exceptions import URLMapException


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    original_url = form.original_url.data
    custom_short = (
        form.custom_short.data.strip() if form.custom_short.data else None
    )
    try:
        url_map = URLMap.create_url_map(original_url, custom_short)
        return render_template(
            'index.html',
            form=form,
            short=url_map.get_short_url(),
            index_url=url_for('index_view')
        )
    except URLMapException as e:
        flash(e.message)
        return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def file_upload_view():
    form = FileUploadForm()
    uploaded = []
    if request.method != 'POST':
        return render_template('files.html', form=form, uploaded=uploaded)
    files = request.files.getlist('files')
    valid_files = [f for f in files if f.filename and f.filename.strip()]
    if not valid_files:
        flash(app.config['NO_FILES_TO_UPLOAD'])
        return render_template('files.html', form=form)

    try:
        public_urls = asyncio.run(async_upload_files_to_yadisk(valid_files))
        file_data = [(
            file.filename, url
        ) for file, url in zip(valid_files, public_urls) if url]
        uploaded = URLMap.batch_create(file_data)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        flash(f'{app.config["FILE_UPLOAD_ERROR"]}: {e}')
        return render_template('files.html', form=form)

    return render_template(
        'files.html',
        form=form,
        uploaded=uploaded,
        files_url=url_for('file_upload_view')
    )


@app.route('/<string:short>')
def redirect_view(short):
    url_map = URLMap.get_by_short(short)
    if url_map:
        return redirect(url_map.original_url)
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND
