#!/bin/sh

echo -n "Dropping wals2013 database... "
psql -c "drop database wals2013"
echo -n "Dropping jpharvest database... "
psql -c "drop database jpharvest"
echo -n "Dropping sil_rcem database... "
psql -c "drop database sil_rcem"

echo -n "Loading WALS... "
psql -c "create database wals2013"
psql wals2013 < wals.sql |
	awk '/^(NOTICE|ERROR|WARN)/'

echo -n "Loading JPHarvest schema... "
psql -c "create database jpharvest"
psql jpharvest < JPHarvest.schema 2>&1 |
	awk '/^(ERROR|WARN)/' |
       	grep -v 'MSysNavPaneGroup' |
	grep -v 'there is no unique constraint matching given keys for referenced table' |
	grep -v 'constraint.*for relation.*already exists"

echo "Loading JPHarvest data"
psql jpharvest < JPHarvest.data 2>&1 |
  awk '
  /INSERT 0 1/ {c++;};
  /^[^ISF]/ {print $0;};
  /^$/ {};
  /^Finished/ {print $3, c, "inserts"; c=0;};'

echo -n "Loading SIL retired code element mappings (sil_rcem) schema"
psql -c "create database sil_rcem"
psql sil_rcem < iso-639-3_Retirements.schema
echo "Loading SIL retired code element mappings (sil_rcem) data"
# Exclude the header row (WITH HEADER not available in tab delim mode)
grep -v 'Ret_Reason.*Ret_Remedy' iso-639-3_Retirements.tab | 
	psql sil_rcem -c "copy Retirements from STDIN"

echo "All done."
