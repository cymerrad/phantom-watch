# phantom-watch

## Kolejny web serwis

Tym razem celem jest śledzenie tego jak zmieniają się strony Uniwersytetu Warszawskiego

## Jak to ma wyglądać?

- Otwarte api do zarządzania tym jaki serwis ma być śledzony (i dla kogo - w przyszłości)
- Jeden serwis zajmuje się kontrolowaniem zawartości bazy danych z użytkownikami, zadaniami i screenshotami
- Drugi żyje sobie w tle, wykonuje zadania, o których dowiaduje się z bazy danych i dodaje do niej efekty swojej pracy
- Jakiś minimalny front w czymkolwiek... Pewnie w html'u by wykorzystać template'y Django
- Prawodopodobnie apka będzize działać na Dockerze i spróbuję uniknąć Nginxa

## TODO

1. Postawić minimalne api do zarządzania treścią bazy danych
1. Zrobić daemona do robienia screenshotów używającego tego co już kiedyś napisałem
    - PhantomJS w repo lub instalacja gdzieś
    - Celery
1. Front

## Start-up

```Shell
virtualenv env
source env/bin/activate

sudo apt install libmysqlclient-dev
pip install -r requirements.txt

python manage.py makemigrations && python manage.py migrate --run-syncdb
celery -A phantom_watch beat -l info --scheduler django_celery_beat.schedulers:DatabseScheduler
python manage.py runserver
```

## Other

http://packages.erlang-solutions.com/site/esl/esl-erlang/FLAVOUR_1_general/esl-erlang_20.3-1~ubuntu~bionic_amd64.deb
https://www.rabbitmq.com/install-debian.html

```Shell
docker run --name=mysql1 -d mysql/mysql-server
```