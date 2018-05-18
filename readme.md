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
1. ~~Zrobić daemona do robienia screenshotów używającego tego co już kiedyś napisałem~~
    - ~~PhantomJS w repo lub instalacja gdzieś~~
    - ~~Celery~~
1. Front
1. ~~CAS~~
1. Django production settings
1. OK permissions system
1. Ansible
1. Parameters passed to phantom (like resolution, username/password for a page)

## Start-up

Works on Ubuntu 18

```Shell
sudo apt install -y virtualenv python3-dev build-essential
virtualenv -p python3 env
source env/bin/activate

sudo apt install -y libmysqlclient-dev mysql-client
pip install -r requirements.txt

sudo apt --fix-broken install -y

cd mysql;
echo "MySQL in [D]ocker or [r]egular?"
select yn in "Docker" "Regular"; do
    case $yn in
        [Dd]* ) ./docker-setup.sh; break;;
        [Rr]* ) ./mysql-setup.sh; break;;
    esac
done

curl -L http://packages.erlang-solutions.com/site/esl/esl-erlang/FLAVOUR_1_general/esl-erlang_20.3-1~ubuntu~$(lsb_release -c | cut -f2)_amd64.deb -o /tmp/esl-erlang.deb
curl -L https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.7.5/rabbitmq-server_3.7.5-1_all.deb -o /tmp/rabbitmq.deb
sudo dpkg -i /tmp/esl-erlang.deb
sudo dpkg -i /tmp/rabbitmq.deb
sudo apt --fix-broken -y install
curl -L https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -o /tmp/phantomjs.tar.bz2
tar -xf /tmp/phantomjs.tar.bz2 -C daemon/webscreenshot/

python manage.py makemigrations service
python manage.py makemigrations daemon
python manage.py migrate service
python manage.py migrate --run-syncdb
python manage.py loaddata users webpages

# finally run three services
celery -A phantom_watch beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler & celery -A phantom_watch worker -l info &
python manage.py runserver

# connect to mysql
mysql service -h 127.0.0.1 -u django -pdjango

# lol
 rm -rf daemon/migrations; yes yes | ./manage.py reset_db; ./manage.py makemigrations daemon; ./manage.py migrate --run-syncdb; ./manage.py loaddata users;

```

## Libraries documentation & tutorials

https://pypi.org/project/django_celery_beat/
http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html
http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-debian-8
