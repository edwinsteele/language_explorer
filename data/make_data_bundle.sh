#!/bin/sh

# Change accordingly
JPHARVEST_LOCATION=~/Code/lex_data/JPHarvestFieldDataOnly.mdb;
JPHARVEST_TABLE_ORDER=~/Code/lex_data/jpharvest-table-insertion-order.txt;
JPHARVEST_SCHEMA_HACKS=~/Code/language_explorer/data/jpharvest_schema_hacks.schema;
WALS_LOCATION=~/Code/lex_data/wals2013.sql;
DATABASE_OWNER=esteele;
CACHE_LOCATION=/Users/esteele/Code/language_explorer/data/.cache;
CENSUS_LANP_ENGLP_LOCATION=~/Code/language_explorer/data/census_2011_LANP_ENGLP.csv;
ISO_639_RETIREMENTS_SCHEMA=~/Code/language_explorer/data/iso-639-3_Retirements.schema;
ISO_639_RETIREMENTS_DATA=~/Code/language_explorer/data/iso-639-3_Retirements.tab;
LOADER_SCRIPT_LOCATION=~/Code/language_explorer/data/load_data_bundle.sh;

# Don't adjust
LEX_DATA_SUBDIR="lex_data_bundle";
LEX_DATA_BUNDLE="lex_data-$(date '+%Y%m%d-%H%M%S').tar.gz";
FINAL_WALS_NAME="wals.sql";
FINAL_JPHARVEST_DATA_NAME="JPHarvest.data";
FINAL_JPHARVEST_SCHEMA_NAME="JPHarvest.schema";

# We use gnu-sed here, because BSD sed doesn't have \U or \L to allow
#  case changes. We also lean on gsed's acceptance of comments anywhere
#  in the line
SED=gsed;

base_dir=$(mktemp -d /tmp/temp.XXXXXX);
echo "### temp dir is $base_dir";
lex_data_dir=$base_dir/$LEX_DATA_SUBDIR;
mkdir $lex_data_dir;

# JPHARVEST
# Extract schema
mdb-schema $JPHARVEST_LOCATION postgres |
	$SED 's/^CREATE UNIQUE INDEX/CREATE INDEX/' > $lex_data_dir/$FINAL_JPHARVEST_SCHEMA_NAME;
# Extract data
for i in $(grep -v "^#" $JPHARVEST_TABLE_ORDER); do
        #echo "Ready to process $i. Enter to start"; read;
        echo "Processing $i... ";
        mdb-export -I postgres -q \' $JPHARVEST_LOCATION $i | $SED '1i\
set DateStyle="MDY";
s/\(RPz[a-z]\)/\U\1/;
s/\(UG[yz][a-z]\)/\U\1/;
s/moeykham...psmail.net/moeykham_psmail.net/; # adjust single quotes that are illegal in data load
' >> $lex_data_dir/$FINAL_JPHARVEST_DATA_NAME
	echo "\\echo Finished processing $i;" >> $lex_data_dir/$FINAL_JPHARVEST_DATA_NAME;
done
# Copy schema hacks
cp $JPHARVEST_SCHEMA_HACKS $lex_data_dir;

# WALS
sed 's/robert/esteele/g
s/^CREATE EXTENSION/--CREATE EXTENSION/
s/^COMMENT ON EXTENSION/--COMMENT ON EXTENSION/' $WALS_LOCATION > $lex_data_dir/$FINAL_WALS_NAME

# Cached files from various scraped sources
mkdir $lex_data_dir/cache;
cp $CACHE_LOCATION/* $lex_data_dir/cache 

# Census
cp $CENSUS_LANP_ENGLP_LOCATION $lex_data_dir;

# ISO 639-3
cp $ISO_639_RETIREMENTS_SCHEMA $lex_data_dir;
cp $ISO_639_RETIREMENTS_DATA $lex_data_dir;

# Loader
cp $LOADER_SCRIPT_LOCATION $lex_data_dir;

# Make the archive
pushd $base_dir > /dev/null;
tar -zcf $LEX_DATA_BUNDLE $LEX_DATA_SUBDIR;
popd > /dev/null;
echo "Archive is available at $base_dir/$LEX_DATA_BUNDLE";
