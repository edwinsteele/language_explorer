# Sources

## Joshua Project
http://www.joshuaproject.net

Database available at:
http://www.joshuaproject.net/assets/data/jpharvfielddataonly.zip (MS Access)
Requires mdbtools

Install with data/load_jpharvest.sh


## WALS
http://wals.info

1. http://github.com/clld/wals-data/blob/master/wals2013.sql.gz (postgres 9.1 dump)
2. psql -c "create database wals2013"
3. sed -i -e 's/robert/esteele/g' ~/Downloads/wals2013.sql
4. psql wals2013 < ~/Downloads/wals2013.sql

pip install git+https://github.com/clld/wals3.git

## Australian Census 2011
http://www.abs.gov.au/websitedbs/censushome.nsf/home/census

Data comes from [ABS TableBuilder](http://www.abs.gov.au/websitedbs/censushome.nsf/home/tablebuilder?opendocument&navpos=240)

1. Select the "2011 Census - Cultural and Language Diversity" Database
2. Under Language Spoken At Home (LANP), drill down to find "Australian Indigenous Languages"
3. Select all at the "LANP - 4 digit level" (237 items)
4. Click "Add to Row"
5. Click "Retrieve Data"
6. Download Table as type "Comma Separated Value (.csv)"

This downloaded file is data/census_2011_LANP.csv