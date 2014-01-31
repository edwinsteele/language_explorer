
Sources
=======

Joshua Project
--------------
http://www.joshuaproject.net

http://www.joshuaproject.net/assets/data/jpharvfielddataonly.zip (MS Access)
Install mdbtools
psql -c "create database jpharvest"
mdb-schema --no-relations ~/Downloads/JPHarvestFieldDataOnly.mdb postgres | psql jpharvest
mdb-schema ~/Downloads/JPHarvestFieldDataOnly.mdb postgres |psql jpharvest

for i in $(mdb-tables ~/Downloads/JPHarvestFieldDataOnly.mdb); do
	echo "Ready to process $i. Enter to start";
	read;
	mdb-export -I postgres -q \' ~/Downloads/JPHarvestFieldDataOnly.mdb $i | sed '1i\
set DateStyle="MDY";' | 
	psql jpharvest;
done

WALS
----
http://wals.info

http://github.com/clld/wals-data/blob/master/wals2013.sql.gz (postgres 9.1 dump)
psql -c "create database wals2013"
sed -i -e 's/robert/esteele/g' ~/Downloads/wals2013.sql
psql wals2013 < ~/Downloads/wals2013.sql

pip install git+https://github.com/clld/wals3.git

