#!/bin/sh

# Makes a static instance of the language explorer site.
# Assumes it is not running.

VENV_BASE="/Users/esteele/.virtualenvs/language_explorer"
BASE_DIR="/Users/esteele/Code/language_explorer"
STATIC_ASSET_BASE="$BASE_DIR/language_explorer"
STATIC_ASSET_DIRNAME="static"
MIRROR_OUTPUT_DIR="/Users/esteele/Sites/lex-mirror"
LIBRARY_OUTPUT_DIR="$MIRROR_OUTPUT_DIR/lib"
LEX_PROTOCOL="http://"
LEX_INSTANCE="127.0.0.1:5000"

rm -rf $MIRROR_OUTPUT_DIR
mkdir -p $MIRROR_OUTPUT_DIR

LANGUAGE_EXPLORER_DEPLOYMENT=staging $VENV_BASE/bin/gunicorn -b $LEX_INSTANCE language_explorer:app &

pushd $MIRROR_OUTPUT_DIR
wget --no-verbose --inet4-only --recursive --level=inf \
	--no-remove-listing --adjust-extension ${LEX_PROTOCOL}${LEX_INSTANCE}

# Collapse host directory (wget --no-host-directories option doesn't seem
#  to collapse)
mv "$MIRROR_OUTPUT_DIR/$LEX_INSTANCE/"* $MIRROR_OUTPUT_DIR
rmdir "$MIRROR_OUTPUT_DIR/$LEX_INSTANCE"
popd

# Convert all hrefs to use .html suffixes (none are present in the
#  dynamic site, so we can assume that this is safe to execute here.
# Don't try to add a .html to hrefs to the root directory
# We use gnu sed here so we have access to the -i argument
find $MIRROR_OUTPUT_DIR -type f | \
	xargs gsed -i 's/href="\(\/[a-z][a-z/]*\)">/href="\1.html">/'

# Copy libraries
mkdir $LIBRARY_OUTPUT_DIR
pushd $STATIC_ASSET_BASE
cp -R $STATIC_ASSET_DIRNAME $MIRROR_OUTPUT_DIR
popd

pkill -f gunicorn
