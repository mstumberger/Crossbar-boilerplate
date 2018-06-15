# WAMP backend boilerplate

- using crossbar.io WAMP router and django ORM with admin panel serving as wsgi


## Database

      sudo su postgres
      
      psql

      CREATE ROLE crossbar SUPERUSER LOGIN REPLICATION CREATEDB CREATEROLE;

      CREATE DATABASE backend OWNER crossbar;

      ALTER USER crossbar WITH PASSWORD 'top_secret';
    
if we need:
    
      dropdb example

## Install dependencies and initialize database

      pip3 install -r requirements.txt
      python3 models/manage.py migrate
      python3 manage.py createsuperuser


---
## Run server without service

    crossbar start
    Open browser http://localhost:8080/admin/

## Run client

    python3 helpers/client.py
    Open web/client.html in browser

---

## Django ORM Standalone Application

How to use?
-----------
+ Generate a new `SECRET_KEY` for your settings.py.
+ Modify settings.py to add your database connection parameters.
+ Open "data/models.py". Modify existing model or add your own.
+ Run `python manage.py makemigrations` to make migration scripts
+ Run `python manage.py migrate` to create the tables and sync db changes. Feel free to use other manage.py commands available for django orm.
+ Every time you make changes to models or change db parameters, don't forget to run the migrations.

---

## MAKE AS A SERVICE
run:

    which crossbar

copy location and run:

    sudo mcedit /etc/systemd/system/crossbar.service
    
paste:
    
    [Unit]
    Description=Crossbar.io router
    After=network.target
    
    [Service]
    Type=simple
    User=ubuntu
    Group=ubuntu
    StandardInput=null
    StandardOutput=journal
    StandardError=journal
    Environment="OPTIONAL_VAR=var"
    ExecStart=/copyed/location/bin/crossbar start --cbdir=/home/crossbar_server/.crossbar
    Restart=on-abort
    
    [Install]
    WantedBy=multi-user.target
    
save and run:

    sudo systemctl daemon-reload

    sudo systemctl enable crossbar.service
    
    sudo systemctl start crossbar
    
if you need:
    
    sudo systemctl restart crossbar
    
    sudo journalctl -f -u crossbar

