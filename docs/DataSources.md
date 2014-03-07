Sources
=======

Joshua Project
--------------
http://www.joshuaproject.net

Database available at:
http://www.joshuaproject.net/assets/data/jpharvfielddataonly.zip (MS Access)

Requires mdbtools


WALS
----
http://wals.info

http://github.com/clld/wals-data/blob/master/wals2013.sql.gz (postgres 9.1 dump)
psql -c "create database wals2013"
sed -i -e 's/robert/esteele/g' ~/Downloads/wals2013.sql
psql wals2013 < ~/Downloads/wals2013.sql

pip install git+https://github.com/clld/wals3.git

