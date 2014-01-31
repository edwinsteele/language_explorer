
Sources
=======

Joshua Project
--------------
http://www.joshuaproject.net

http://www.joshuaproject.net/assets/data/jpharvfielddataonly.zip (MS Access)
Install mdbtools
psql -c "create database jpharvest"
# decided not to use egrep for readability
mdb-schema ~/Downloads/JPHarvestFieldDataOnly.mdb postgres |
	grep -v 'CREATE UNIQUE INDEX "tblGEO4StatesProvinces_ROG3_idx"' |
	grep -v 'CREATE UNIQUE INDEX "tblLNG7DialectAlternateNames_ROL4_idx"' |
	grep -v 'CREATE UNIQUE INDEX "tblLnkPEOtoGEO_ROG3_idx")' |
	grep -v 'CREATE UNIQUE INDEX "tblLnkPEOtoGEOLocationInCountry_ROG3_idx"' |
	psql jpharvest

for i in $(grep -v "^#" jpharvest-table-insertion-order.txt); do
	echo "Ready to process $i. Enter to start";
	read;
	mdb-export -I postgres -q \' ~/Downloads/JPHarvestFieldDataOnly.mdb $i | sed '1i\
set DateStyle="MDY";' | 
	psql jpharvest | awk '/INSERT 0 1/ {c++;}; /^[^I]/ {print $0;} END {print c " inserts";}'
done

WALS
----
http://wals.info

http://github.com/clld/wals-data/blob/master/wals2013.sql.gz (postgres 9.1 dump)
psql -c "create database wals2013"
sed -i -e 's/robert/esteele/g' ~/Downloads/wals2013.sql
psql wals2013 < ~/Downloads/wals2013.sql

pip install git+https://github.com/clld/wals3.git

