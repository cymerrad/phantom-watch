sudo docker pull mysql/mysql-server
sudo docker run --name=mysql1 -d mysql/mysql-server
sudo docker logs mysql1 2>&1 | grep GENERATED
sudo docker exec -it mysql1 mysql -uroot -p