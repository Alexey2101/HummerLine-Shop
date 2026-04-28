# Развёртывание на Railway — хранение пользовательских изображений

Этот файл содержит шаги для настройки хранения пользовательских загружаемых файлов (медиа) на Railway с использованием Railway Buckets (S3-совместимые) или внешнего S3.

1) Создайте Railway Bucket
- В панели Railway: `Storage` -> `Create Bucket`.
- Скопируйте `Access Key`, `Secret` и `Bucket name`. Также запишите `Endpoint` если доступен.

2) Добавьте переменные окружения в Railway (Project → Variables)
- `USE_S3` = `true`
- `AWS_ACCESS_KEY_ID` = <access_key>
- `AWS_SECRET_ACCESS_KEY` = <secret>
- `AWS_STORAGE_BUCKET_NAME` = <bucket_name>
- (опционально) `AWS_S3_ENDPOINT_URL` = <https://...> — указать только для S3-совместимого хранилища (Railway Buckets)

Остальные настройки (регион, CORS, кастомный домен) не обязательны для базовой работы и обычно не нужны для простого кейса на Railway.

Важно: для хоста https://hummerline.up.railway.app установите в Variables:
- `RAILWAY_PUBLIC_DOMAIN` = `hummerline.up.railway.app`

И убедитесь, что в `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` настроен этот домен (в проекте уже добавлен по умолчанию).

3) Настройте CORS для Bucket
- В панели Storage задайте правила CORS, разрешающие ваши домены (например `https://hummerline-shop-production.up.railway.app`) и методы `GET`/`PUT`/`POST`/`DELETE` при необходимости.

4) Миграции и static
- Запустите миграции и соберите статику в процессе деплоя (Railway Run/Build commands):
```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Railway командa деплоя (пример) — укажите эти команды в разделе Deploy → Settings → Build/Run commands:

Build command:
```bash
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Start command (Procfile присутствует, Railway запустит `web`):
```bash
gunicorn core.wsgi --log-file -
```

5) Проверка из Django (локально)
- Скопируйте переменные в файл `.env` или в окружение и запустите локально:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
- Попробуйте загрузить изображение через форму добавления объявления — если `USE_S3=true`, файл должен появиться в бакете.

6) Health-check (встроенная команда)
- В проект добавлена команда управления `check_s3`, которая проверяет доступ к бакету и может загрузить временный объект.
- Как запустить:
```bash
python manage.py check_s3
```

7) Дополнительно: CDN и кастомные домены
- Если вы хотите раздавать медиа через CDN или кастомный домен, укажите `AWS_S3_CUSTOM_DOMAIN` и настройте CNAME в вашем DNS, указывающий на endpoint или CDN.
- Убедитесь, что `AWS_S3_CUSTOM_DOMAIN` добавлен в `ALLOWED_HOSTS` при использовании подписанных URL.

Если хотите, могу автоматически добавить `collectstatic` и `migrate` в Railway Deploy commands примеры или настроить GitHub Actions для CI/CD. Напишите, что предпочитаете.