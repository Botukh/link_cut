### LinkCut — это веб-приложение на Flask, которое позволяет:

- сокращать длинные ссылки, работая через веб-интерфейс или API,

- асинхронно загружать файлы на диск и получать короткие публичные ссылки на них через веб-инерфейс.


## Как запустить проект LinkCut:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Botukh/link_cut
cd link_cut
```
Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать в директории проекта файл .env с четыремя переменными окружения:

```
FLASK_APP=yacut
FLASK_ENV=development
SECRET_KEY=your_secret_key
DB=sqlite:///db.sqlite3
DISK_TOKEN=your_yandex_disk_oauth_token
```

Создать базу данных и применить миграции:

```
flask db upgrade
```

Запустить проект:

```
flask run
```
После запуска перейдите в браузере по [адресу](http://127.0.0.1:5000/)

Примеры запросов к API, варианты ответов и ошибок приведены в спецификации openapi.yml; спецификация есть в репозитории yacut. 
Для удобной работы с документом воспользуйтесь онлайн-редактором Swagger Editor

## Технологический стэк:

 - Python
 - Flask
 - SQLAlchemy
 - Flask-Migrate
 - Flask-WTF
 - Alembic
 - aiohttp (асинхронная загрузка файлов)
 - Bootstrap 5 (UI)
 - SQLite (по умолчанию)

  Разработка      | *Ботух Юлия*     | [Telegram](https://t.me/botuh) |
