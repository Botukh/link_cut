import asyncio
from flask import (
    Blueprint, render_template, flash, redirect, request
)
from werkzeug.utils import secure_filename

from .forms import URLForm
from .models import URLMap, FileMap
from .utils import get_unique_short_id
from .ydisk import upload_file_to_disk
from . import db

main_bp = Blueprint('main', __name__)


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
    uploaded = []

    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files or files == [None]:
            flash("Файлы не выбраны", "danger")
            return render_template('files.html', uploaded=uploaded)

        async def process_files():
            tasks = []
            for file in files:
                if file.filename == '':
                    continue
                filename = secure_filename(file.filename)
                ydisk_path = f"app_uploads/{filename}"
                short_id = get_unique_short_id()
                file_data = file.read()

                async def handle_upload():
                    try:
                        await upload_file_to_disk(file_data, ydisk_path)
                        file_entry = FileMap(
                            filename=filename,
                            ydisk_path=ydisk_path,
                            short=short_id
                        )
                        db.session.add(file_entry)
                        uploaded.append((filename, short_id))
                    except Exception as e:
                        flash(f"Ошибка загрузки {filename}: {str(e)}", "danger")

                tasks.append(handle_upload())

            await asyncio.gather(*tasks)

        asyncio.run(process_files())

        if uploaded:
            db.session.commit()
            flash("Загрузка завершена", "success")

    return render_template('files.html', uploaded=uploaded)


@main_bp.route('/<string:short>')
def redirect_view(short):
    link = URLMap.query.filter_by(short=short).first()
    if link:
        return redirect(link.original)
    return render_template('errors/404.html'), 404


@main_bp.route('/f/<string:short>')
def download_file_redirect(short):
    file_entry = FileMap.query.filter_by(short=short).first()
    if not file_entry:
        return render_template('errors/404.html'), 404
    return redirect(f"https://disk.yandex.ru/d/{file_entry.ydisk_path}")
