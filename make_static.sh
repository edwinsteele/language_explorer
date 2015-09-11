#!/bin/sh

# Makes a static instance of the language explorer site.

MIRROR_OUTPUT_DIR="/Users/esteele/Sites/lex-mirror"
LEX_PROTOCOL="http://"
LEX_INSTANCE="localhost:8000"

rm -rf $MIRROR_OUTPUT_DIR
mkdir -p $MIRROR_OUTPUT_DIR

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
