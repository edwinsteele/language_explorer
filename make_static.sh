#!/bin/sh

# Makes a static instance of the language explorer site.
# Assumes it is not running.

# To allow deployment to a subdirectory of www.wordspeak.org
DEPLOYMENT_PREFIX="/language_explorer"
VENV_BASE="/Users/esteele/.virtualenvs/language_explorer"
BASE_DIR="/Users/esteele/Code/language_explorer"
STATIC_ASSET_BASE="$BASE_DIR/language_explorer"
STATIC_ASSET_DIRNAME="static"
MIRROR_OUTPUT_DIR="/Users/esteele/Sites/lex-mirror$DEPLOYMENT_PREFIX"
LIBRARY_OUTPUT_DIR="$MIRROR_OUTPUT_DIR/lib"
LEX_PROTOCOL="http://"
LEX_INSTANCE="127.0.0.1:8000"

rm -rf $MIRROR_OUTPUT_DIR
mkdir -p $MIRROR_OUTPUT_DIR

LANGUAGE_EXPLORER_DEPLOYMENT=staging $VENV_BASE/bin/gunicorn -b $LEX_INSTANCE language_explorer:app &

# Give it time to startup
sleep 3

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
# Don't try to add a .html to hrefs to the root director
# We use gnu sed here so we have access to the -i argument
find $MIRROR_OUTPUT_DIR -type f | \
	xargs gsed -i 's/href="\(\/[a-z][a-z/]*\)">/href="\1.html">/'

# Adjust hrefs, action and src elements to be prefixed with the deployment
#  prefix (if one is used)
if [ -n "$DEPLOYMENT_PREFIX" ]; then
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/href="/href="\'$DEPLOYMENT_PREFIX'/'
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/src="/src="\'$DEPLOYMENT_PREFIX'/'
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/action="/action="\'$DEPLOYMENT_PREFIX'/'
fi


# Copy libraries
mkdir $LIBRARY_OUTPUT_DIR
pushd $STATIC_ASSET_BASE
cp -R $STATIC_ASSET_DIRNAME $MIRROR_OUTPUT_DIR
popd

pkill -f gunicorn
