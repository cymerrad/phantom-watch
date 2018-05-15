sudo apt install -y virtualenv python3-dev build-essential
virtualenv -p python3 env
source env/bin/activate

sudo apt install -y libmysqlclient-dev mysql-client
pip install -r requirements.txt

sudo apt --fix-broken install -y

cd mysql;
echo "MySQL in [D]ocker or [r]egular?"
while read option; do
    case $option in
        ""  ) echo "Default is Docker"; ./docker-setup.sh; break;;
        [Dd]* ) ./docker-setup.sh; break;;
        [Rr]* ) ./mysql-setup.sh; break;;
    esac
done
cd ..

curl -L http://packages.erlang-solutions.com/site/esl/esl-erlang/FLAVOUR_1_general/esl-erlang_20.3-1~ubuntu~bionic_amd64.deb -o /tmp/esl-erlang.deb
curl -L https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.7.5/rabbitmq-server_3.7.5-1_all.deb -o /tmp/rabbitmq.deb
sudo dpkg -i /tmp/esl-erlang.deb
sudo dpkg -i /tmp/rabbitmq.deb
curl -L https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 -o /tmp/phantomjs.tar.bz2
tar -xf /tmp/phantomjs.tar.bz2 -C daemon/webscreenshot/

python manage.py makemigrations service
python manage.py makemigrations daemon
python manage.py migrate service
python manage.py migrate --run-syncdb