#!/bin/bash
#System setup script

echo "Installing system requirements"
sudo pip install IPIMS_Django_Source_Files/ipcms/requirements.txt

echo "Making database migrations"
python IPIMS_Django_Source_Files/ipcms/manage.py makemigrations

echo "Finalizing migrations"
python IPIMS_Django_Source_Files/ipcms/manage.py migrate

echo "Running server on port 8000 localhost"
python IPIMS_Django_Source_Files/ipcms/manage.py runserver
