#!/usr/bin/env bash
apt-get update
apt-get install -y python-pip libpq-dev python-dev postgresql postgresql-contrib
service postgresql start
sudo -u postgres createuser tsundiary
sudo -u postgres createdb tsundiary
sudo -u postgres psql -U postgres -d postgres -c "alter user tsundiary with password 'baka';"
