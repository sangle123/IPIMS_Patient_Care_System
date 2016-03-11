#!/bin/bash
#Unit testing run script

#mv IPIMS_Django_Source_Files/ipcms/test_INTEGRATION_TEST.py IPIMS_Django_Source_Files/ipcms/#test_INTEGRATION_TEST.py
#mv IPIMS_Django_Source_Files/ipcms/test_SYSTEM_TEST.py IPIMS_Django_Source_Files/ipcms/#test_SYSTEM_TEST.py


cd IPIMS_Django_Source_Files/ipcms

sudo mv test_UNIT_TEST.py \#test_UNIT_TEST.py
sudo mv test_SYSTEM_TEST.py \#test_SYSTEM_TEST.py

./manage.py test

sudo mv \#test_UNIT_TEST.py test_UNIT_TEST.py
sudo mv \#test_SYSTEM_TEST.py test_SYSTEM_TEST.py

