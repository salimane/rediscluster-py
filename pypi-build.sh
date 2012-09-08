#! /bin/sh
python setup.py sdist upload
python2.7 setup.py bdist_egg upload --quiet
python2.7 setup.py bdist_wininst --target-version=2.7 --plat-name=win32 register upload --quiet
. /home/salimane/htdocs/env/rediscluster3/bin/activate
python3.2 setup.py bdist_egg upload --quiet
python3.2 setup.py bdist_wininst --target-version=3.2 --plat-name=win32 register upload --quiet
deactivate
