#!/bin/sh

# Makes a static instance of the language explorer site.

MIRROR_OUTPUT_DIR="/Users/esteele/Sites/lex-mirror"
LEX_PROTOCOL="http://"
LEX_INSTANCE="localhost:8000"

rm -rf $MIRROR_OUTPUT_DIR
mkdir -p $MIRROR_OUTPUT_DIR

pushd $MIRROR_OUTPUT_DIR
wget --no-verbose --inet4-only --recursive --level=inf --no-remove-listing --adjust-extension ${LEX_PROTOCOL}${LEX_INSTANCE}

# Adjust anchors to use html suffix

# Collapse host directory (wget --no-host-directories option doesn't seem to collapse)
#pushd $LEX_INSTANCE
#tar -cf - * | (popd; tar -xvf -);
mv "$MIRROR_OUTPUT_DIR/$LEX_INSTANCE/"* $MIRROR_OUTPUT_DIR
rm "$MIRROR_OUTPUT_DIR/$LEX_INSTANCE"
popd
