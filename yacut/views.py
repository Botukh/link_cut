from http import HTTPStatus

from flask import render_template, request, redirect, flash, url_for

from . import app
from .forms import URLMapForm, FileUploadForm
from .models import URLMap
from .ydisk import async_upload_files_to_yadisk
from .models import URLMapValidationError

NO_FILES_TO_UPLOAD = 'Нет файлов для загрузки'
FILE_UPLOAD_ERROR = 'Ошибка загрузки файлов'


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('index.html', form=form)
    original = form.original_link.data
    custom_id = form.custom_id.data
    try:
        return render_template(
            'index.html',
            form=form,
            short=URLMap.create(original, custom_id).get_short_url(),
            index_url=url_for('index_view')
        )
    except URLMapValidationError as e:
        flash(str(e))
        return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def file_upload_view():
    form = FileUploadForm()

    if not form.validate_on_submit():
        return render_template('files.html', form=form, uploaded=[])
    files = request.files.getlist('files')
    if not files or not any(f.filename and f.filename.strip() for f in files):
        flash(NO_FILES_TO_UPLOAD)
        return render_template('files.html', form=form)
    try:
        public_urls = async_upload_files_to_yadisk(files)
        uploaded = URLMap.batch_create([
            (file.filename, url) for file, url in zip(
                files, public_urls) if url
        ])
    except Exception as e:
        flash(f'{FILE_UPLOAD_ERROR}: {e}')
        return render_template('files.html', form=form)

    return render_template(
        'files.html',
        form=form,
        uploaded=uploaded,
        files_url=url_for('file_upload_view')
    )


@app.route('/<string:short>')
def redirect_view(short):
    url_map = URLMap.get(short)
    if url_map:
        return redirect(url_map.original)
    return render_template('errors/404.html'), HTTPStatus.NOT_FOUND
