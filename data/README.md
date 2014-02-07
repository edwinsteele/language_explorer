
Sources
=======

Joshua Project
--------------
http://www.joshuaproject.net

http://www.joshuaproject.net/assets/data/jpharvfielddataonly.zip (MS Access)
Install mdbtools
psql -c "create database jpharvest"
# UNIQUE constraints cause violations of integrity constraints, and are
#  quite possibly due to a bug in mdbtools (perhaps because I don't understand
#  the mdb schema too, so change them so that the uniqueness constraint
#  is removed
# - MSysNavPaneGroup tables are removed as they're not necessary
# - There are a few errors for missing unique constraints on three tables,
#   tblLnkPEOtoGEO, tblLnkPEOtoGEOReligions and tblProgressStatusValues
# - There are 2 errors for duplicate constraint declarations for constraints,
#   tblLnkPEOtoGEOProgressStatus_StatusType_fk and tblLNG6LanguageAlternateNames_ROL3_fk
#
# Otherwise it should be error free
mdb-schema ~/Downloads/JPHarvestFieldDataOnly.mdb postgres |
	sed 's/^CREATE UNIQUE INDEX/CREATE INDEX/' |
	psql jpharvest |
	awk '/^(NOTICE|ERROR|WARN)/' | grep -v 'MSysNavPaneGroup'

# We use gnu-sed here, because BSD sed doesn't have \U or \L to allow
#  case changes
# - Change to date format (mdb-tools exports this db in MDY format)
# - Fix some case sensitivity issues (mixed case to upper case)
#   (these changes will land from upstream by march or april 2014)
for i in $(grep -v "^#" jpharvest-table-insertion-order.txt); do
	#echo "Ready to process $i. Enter to start"; read;
	echo -n "Processing $i... ";
	mdb-export -I postgres -q \' ~/Downloads/JPHarvestFieldDataOnly.mdb $i | gsed '1i\
set DateStyle="MDY";
s/\(RPz[a-z]\)/\U\1/;
s/\(UG[yz][a-z]\)/\U\1/;
' | 
	psql jpharvest | awk '/INSERT 0 1/ {c++;}; /^[^IS]/ {print $0;}; /^$/ {}; END {print c " inserts";}'
done

# Need to update rows in tblLNG6LanguageAlternateNames where ROG3 is NULL (to allow SqlSoup to work)
#  then add a primary key on (probably) ROG3+ROL3+LangAltName
psql jpharvest -c 'delete from "tblLNG6LanguageAlternateNames" where "ROG3" is NULL;'
psql jpharvest -c 'alter table "tblLNG6LanguageAlternateNames" add constraint "tblLNG6LanguageAlternateNames_pkey" PRIMARY KEY ("ROG3","ROL3", "LangAltName");'

WALS
----
http://wals.info

http://github.com/clld/wals-data/blob/master/wals2013.sql.gz (postgres 9.1 dump)
psql -c "create database wals2013"
sed -i -e 's/robert/esteele/g' ~/Downloads/wals2013.sql
psql wals2013 < ~/Downloads/wals2013.sql

pip install git+https://github.com/clld/wals3.git

