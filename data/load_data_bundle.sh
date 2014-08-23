#!/bin/sh

echo -n "Dropping wals2013 database... "
psql -c "drop database wals2013"
echo -n "Dropping jpharvest database... "
psql -c "drop database jpharvest"
echo -n "Dropping sil_rcem database... "
psql -c "drop database sil_rcem"

echo "Loading WALS"
psql -c "create database wals2013"
psql wals2013 < wals.sql |
	awk '/^(NOTICE|ERROR|WARN)/'

echo "Loading JPHarvest schema"
psql -c "create database jpharvest"
psql jpharvest < JPHarvest.schema 2>&1 |
	awk '/^(ERROR|WARN)/' |
       	grep -v 'MSysNavPaneGroup'

echo "Loading JPHarvest data"
psql jpharvest < JPHarvest.data 2>&1 |
  awk '
  /INSERT 0 1/ {c++;};
  /^[^ISF]/ {print $0;};
  /^$/ {};
  /^Finished/ {print $3, c, " inserts"; c=0;};'

echo "Loading SIL retired code element mappings (sil_rcem) schema"
psql -c "create database sil_rcem"
psql sil_rcem < iso-639-3_Retirements.schema
echo "Loading SIL retired code element mappings (sil_rcem) data"
psql sil_rcem < iso-639-3_Retirements.tab
