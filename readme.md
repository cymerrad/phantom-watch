# phantom-watch

## Kolejny web serwis

Tym razem celem jest śledzenie tego jak zmieniają się strony Uniwersytetu Warszawskiego

## Jak to ma wyglądać?

- Otwarte api do zarządzania tym jaki serwis ma być śledzony (i dla kogo - w przyszłości)
- Jeden serwis zajmuje się kontrolowaniem zawartości bazy danych z użytkownikami, zadaniami i screenshotami
- Drugi żyje sobie w tle, wykonuje zadania, o których dowiaduje się z bazy danych i dodaje do niej efekty swojej pracy
- Jakiś minimalny front w czymkolwiek... Pewnie w html'u by wykorzystać template'y Django
- Spróbuję uniknąć Nginxa i zwyczajowego ohydnego set-up'u

## TODO

1. ~~Postawić minimalne api do zarządzania treścią bazy danych~~
1. Zrobić daemona do robienia screenshotów używającego tego co już kiedyś napisałem
    - PhantomJS w repo lub instalacja gdzieś
    - Celery
1. Front

## Start-up

```Shell
virtualenv -p python3 env
source env/bin/activate

sudo apt install -y libmysqlclient-dev mysql-client
pip install -r requirements.txt

sudo snap install docker
sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
cd mysql; sudo docker-compose up -d; cd ..

curl -L http://packages.erlang-solutions.com/site/esl/esl-erlang/FLAVOUR_1_general/esl-erlang_20.3-1~ubuntu~bionic_amd64.deb -o /tmp/esl-erlang.deb
curl -L https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.7.5/rabbitmq-server_3.7.5-1_all.deb -o /tmp/rabbitmq.deb
sudo dpkg -i /tmp/esl-erlang.deb
sudo dpkg -i /tmp/rabbitmq.deb

python manage.py makemigrations service
python manage.py makemigrations daemon
python manage.py migrate service
python manage.py migrate --run-syncdb
python manage.py loaddata users webpages

# finally run three services
celery -A phantom_watch beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
celery -A phantom_watch worker -l info &
python manage.py runserver
```

## Links with some downloads

http://packages.erlang-solutions.com/site/esl/esl-erlang/FLAVOUR_1_general/esl-erlang_20.3-1~ubuntu~bionic_amd64.deb
https://www.rabbitmq.com/install-debian.html
