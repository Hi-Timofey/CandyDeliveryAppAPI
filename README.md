# Задача - Candy Delivery App API
---
## Вступление
Чтобы немного скрасить жизнь людей на самоизоляции, вы решаете открыть
интернет-магазин по доставке конфет *"Сласти от всех напастей"*.
## Постановка задачи
Ваша задача — разработать на python *REST API* сервис, который позволит нанимать курьеров на работу,
    принимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.
    Сервис необходимо развернуть на предоставленной виртуальной машине на 0.0.0.0:8080.

    ---
## Требования ПО
    Для корректной работы  веб сервера необходимо установить:

    * [Python 3](https://python.org/)
    * Зависимости для Python из файла **requirements.txt**
    * Docker (опционально)

    ---
## Установка  
### Если установка просиходит не на Ubuntu, то шаги установки могут отличаться. Необходимо установить Python 3 и зависимотси в отдельном порядке при помощи пакетного менеджера дистрибутива или на [сайте python.org](https://python.org/)

    Установку необходимых зависимостей можно выполнить автоматически при помощи скрипта *install.sh*:

    $ sh install_local.sh

    *или*

    $ chmod u+x install_local.sh
    $ ./install_local.sh

    В процессе установки будет скачан:

* Python 3 (на cервере с Ubuntu)  
* Pip 
* Python Virtualenv 
* Flask и зависимости к нему
* Pytest для тестирования
* Docker + Docker-compose (для контейнеризации)


Также необходимо поменять секретный ключ и режим работы сервера в конфигурационном файле сервера *api/config.cfg*:

        SECRET_KEY = 'вставить_случайную_последовательность_символов'	
        ...
        DEBUG = False

---
## Запуск (Docker)
    Для запуска через Docker небходимо:

* Docker
* Docker-compose

Установка (включена в скрипт *install_local.sh*):

        $ sudo apt -y update && sudo apt -y upgrade
        $ sudo apt install apt-transport-https ca-certificates curl software-properties-common
        $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
        $ sudo apt update && apt-cache policy docker-ce
        $ sudo apt -y install docker-ce docker-compose
        $ sudo docker run hello-world # Проверка работоспособности

Для запуска веб сервера достаточно в папке проекта выполнить команду:

        $ docker-compose up -d --build

## Запуск обычный
### Подготовка
Перед началом работы с сервером необходим активировать venv:

        $ source .flask_env/bin/activate

из которого в последствии можно выйти:

            $ deactivate

### Тесты
Для запуска тестов используется следующая команда (*пердварительно активировать venv*):

            $ python3 -m pytest 	

После её выполнения может остаться тестовый вариант sqlite бд, который необходимо удалить для дальнейшего корректного функционирования тестов.

### Запуск веб сервера
Для запуска сервера использовать скрипт *./run*:

            $ chmod u+x run.sh
            $ ./run.sh

(при использвании *run.sh* перед сервером будут запущены тесты)
Для запуска без тестов:

            (.flask_env)$ python3 app.py

---
