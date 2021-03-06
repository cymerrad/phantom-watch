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
    - ~~Celery~~
    - ~~Puppeteer~~
1. Front
1. ~~CAS~~
1. ~~Django production settings~~
1. OK permissions system
1. Ansible
1. ~~Puppeteer~~
    - obejście wkurzających pop-upów na niektórych stronach (ostrzeżenie o cookies lub promocje)
    - ~~pre-zdefiniowane widoki (jak z telefonu komórkowego czy tableta)~~
1. Pozbyć się brandingu DRF z /api/
1. https://pypi.org/project/django_celery_results/
1. http://docs.celeryproject.org/en/latest/userguide/workers.html

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

cd daemon/puppet_screenshot
curl -L https://nodejs.org/dist/v8.11.2/node-v8.11.2-linux-x64.tar.xz -o /tmp/node-v8.11.2-linux-x64.tar.xz
sudo tar -xf /tmp/node-v8.11.2-linux-x64.tar.xz -C /opt/
sudo ln -s /opt/node-v8.11.2-linux-x64/bin/npm /usr/bin/npm
sudo ln -s /opt/node-v8.11.2-linux-x64/bin/node /usr/bin/nodejs
sudo ln -s /opt/node-v8.11.2-linux-x64/bin/node /usr/bin/node
npm i
sudo apt install chromium-browser
cd -

python manage.py makemigrations service
python manage.py makemigrations daemon
python manage.py migrate service
python manage.py migrate --run-syncdb
python manage.py loaddata users webpages

# prod
sudo chown -R root:root etc django_host.conf
sudo chmod +x etc/init.d/celery*
sudo cp -r etc/* etc
sudo /etc/init.d/celeryd start && sudo /etc/init.d/celerybeat start

sudo apt install apache2
sudo cp django_host.conf /etc/apache2/sites-available/
sudo a2ensite django_host.conf
sudo systemctl restart apache2

# dev
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
