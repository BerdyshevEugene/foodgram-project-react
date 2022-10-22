# Foodgram project
____
## Description
The foodgram project is designed to create and share recipes. Users can create their own recipes, subscribe to other authors, download recipes, and add recipes to favorites.

## Technology stack
![github](https://camo.githubusercontent.com/6b7f701cf0bea42833751b754688f1a27b6090fdf90bf2b226addff01be817f0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f636b65722d2532333064623765642e7376673f7374796c653d666f722d7468652d6261646765266c6f676f3d646f636b6572266c6f676f436f6c6f723d7768697465) ![github](https://camo.githubusercontent.com/5473e0d3006bb7e662bdf754d830a026ce050be61f1cbbd4689783ae49950b93/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646a616e676f2d2532333039324532302e7376673f7374796c653d666f722d7468652d6261646765266c6f676f3d646a616e676f266c6f676f436f6c6f723d7768697465) ![github](https://camo.githubusercontent.com/cbef21adebc167fac6552145a03c9e12ae03b8afd5e4f7de52379a98297de3fe/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f444a414e474f2d524553542d6666313730393f7374796c653d666f722d7468652d6261646765266c6f676f3d646a616e676f266c6f676f436f6c6f723d776869746526636f6c6f723d666631373039266c6162656c436f6c6f723d67726179) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
____

## Installation

clone the repository and go to it on the command line:
```sh
https://github.com/BerdyshevEugene/foodgram-project-react.git
```

create and activate virtual enviroment:
```sh
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
```

create and fullfill .env file in infra/:
```sh
DB_ENGINE=django.db.backends.postgresq
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

on a remote server install docker:
```sh
sudo apt install docker.io 
```
install docker-compose:
```sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
copy the docker-compose files.yml and nginx.conf from the infra directory to the server:
```sh
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
add secrets GitHub for workflow:
```sh
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<name of db postgres>
DB_USER=<db user>
DB_PASSWORD=<password>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_USERNAME=<username>
DOCKER_PASSWORD=<DockerHub password>

SECRET_KEY=<django secret key>

USER=<username for server connection>
HOST=<IP>
PASSPHRASE=<password for host>
SSH_KEY=<SSH key (command for check: cat ~/.ssh/id_rsa)>
```
if necessary, delete the old information on the server:
```sh
sudo docker stop $(docker ps -qa) && docker rm $(docker ps -qa) && docker rmi -f $(docker images -qa ) && docker volume rm $(docker volume ls -q) && docker network rm $(docker network ls -q)
```
on the server, build docker-compose and make migrations:
```sh
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
```
create superuser:
```sh
sudo docker-compose exec backend python manage.py createsuperuser
```

you can go to the project by following the next link:
http://51.250.86.6/
____

## Author
frontend: Yandex

backend: Eugene Berdyshev

![Build Status](https://github.com/BerdyshevEugene/foodgram-project-react/workflows/main/badge.svg)
