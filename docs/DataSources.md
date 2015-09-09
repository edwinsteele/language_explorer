# Sources

## WALS
http://wals.info

A postgres 9.1 dump is available:

`curl https://raw.githubusercontent.com/clld/wals-data/master/wals2013.sql.gz | gzip -d | sed -i -e 's/robert/esteele/g' > ~/Code/language_explorer/data/wals.sql`  

**Loading is done in a subsequent step**

## Australian Census 2011
http://www.abs.gov.au/websitedbs/censushome.nsf/home/census

Data comes from [ABS TableBuilder](http://www.abs.gov.au/websitedbs/censushome.nsf/home/tablebuilder?opendocument&navpos=240)

1. Select the "2011 Census - Cultural and Language Diversity" Database
2. Under Language Spoken At Home (LANP), drill down to find "Australian Indigenous Languages"
3. Select all at the "LANP - 4 digit level" (237 items)
4. Click "Add to Row"
5. Under Proficiency in Spoken English (ENGLP), select all at level "ENGLP" (7 items). (we choose ENGLP rater than ENGP because we are interested in those that do not speak english at home - http://www.abs.gov.au/ausstats/abs@.nsf/Lookup/2901.0Chapter3302011)
6. Click "Add to Column"
5. Click "Retrieve Data"
6. Download Table as type "Comma Separated Value (.csv)"

This downloaded file is `data/census_2011_LANP_ENGLP.csv` and is accessed in-place, so no further action is required.


## Ethnologue Retired Code Element Mappings
http://www-01.sil.org/iso639-3/

This file contains language codes that have been retired or split.

1. http://www-01.sil.org/iso639-3/iso-639-3_Retirements.tab
2. http://www-01.sil.org/iso639-3/iso-639-3_Retirements.schema

The downloaded file is `data/iso-639-3_Retirements.tab`
The schema file is adapted for postgres from the documentation page above

**Loading is done in a subsequent step** 

## Loading WALS and Ethnologue RCEM

1. `cd data`
2. `./load_data_bundle.sh`  (ignore all JPHarvest related errors)
3. Proceed to the JP Harvest step below

### Joshua Project
http://www.joshuaproject.net

1. Make sure `mdbtools` are installed (database is in MS Access format)
2. Download database from 
`http://joshuaproject.net/assets/media/data/jpharvfielddataonly.zip` and unzip (output file is `JPHarvestFieldDataOnly.mdb`).
3. run `./data/load_jpharvest.sh JPHarvestFieldDataOnly.mdb`

Note (8 Sep 2015): Seems `tblGEO*`, `tblLnkPEOtoGEOLocationInCountry`, `tblLnkPEOtoGEOStateProvince` tables have been removed since 2013 but I don't think I use them so it probably isn't a problem (just remove them from jpharvest-table-insertion-order.txt?)


## Creating and loading a data bundle
The data loading process is scripted, but relies on the resources above being
available. Once they have been downloaded, edit the locations in `data/make_data_bundle.sh` and run the script. The script prints the location of the created data bundle upon completion. Copy the bundle to the target machine and unpack it. Once unpacked, run the `load_data_bundle.sh` script that is inside the bundle.

