#! /bin/sh
. /home/salimane/htdocs/env/rediscluster2.7/bin/activate
python setup.py sdist upload
python setup.py bdist_egg upload --quiet
python setup.py bdist_wininst --target-version=2.7 --plat-name=win32 register upload --quiet
deactivate
. /home/salimane/htdocs/env/rediscluster3.2/bin/activate
python setup.py bdist_egg upload --quiet
python setup.py bdist_wininst --target-version=3.2 --plat-name=win32 register upload --quiet
deactivate
