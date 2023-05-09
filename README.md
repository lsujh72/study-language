## Cloning & Run Linux:

- `git clone https://github.com/lsujh72/study-language.git`

- `cd study-language`

- `poetry install`

- `python3 manage.py migrate`

- `python3 manage.py createsuperuser`

- `python3 manage.py runserver`

- `celery -A study_language worker -l info`
