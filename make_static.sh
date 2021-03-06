#!/bin/sh

# Makes a static instance of the language explorer site.
# Assumes it is not running.

# To allow deployment to a subdirectory of www.wordspeak.org
#DEPLOYMENT_PREFIX="/language_explorer"
DEPLOYMENT_PREFIX=""
VENV_BASE="/Users/esteele/.virtualenvs/language_explorer"
BASE_DIR="/Users/esteele/Code/language_explorer"
STATIC_ASSET_BASE="$BASE_DIR/language_explorer"
STATIC_ASSET_DIRNAME="static"
MIRROR_OUTPUT_DIR="/usr/local/var/www/lex-mirror"
#MIRROR_OUTPUT_DIR="/Users/esteele/Sites/staging.wordspeak.org/$DEPLOYMENT_PREFIX"
LIBRARY_OUTPUT_DIR="$MIRROR_OUTPUT_DIR/lib"
LEX_PROTOCOL="http://"
LEX_INSTANCE="127.0.0.1:8000"
SEARCH_FORM_DEST="/search"

rm -rf $MIRROR_OUTPUT_DIR
mkdir -p $MIRROR_OUTPUT_DIR

LANGUAGE_EXPLORER_DEPLOYMENT=staging $VENV_BASE/bin/gunicorn -b $LEX_INSTANCE language_explorer:app &

# Give it time to startup
sleep 3

pushd $MIRROR_OUTPUT_DIR
wget --no-verbose --inet4-only --recursive --level=inf \
	--no-remove-listing --adjust-extension ${LEX_PROTOCOL}${LEX_INSTANCE}
# Search form is only accessible via a form, so needs to be scraped separately
wget --no-verbose --inet4-only --no-remove-listing \
	--adjust-extension ${LEX_PROTOCOL}${LEX_INSTANCE}${SEARCH_FORM_DEST}

# Collapse host directory (wget --no-host-directories option doesn't seem
#  to collapse)
mv "$MIRROR_OUTPUT_DIR/$LEX_INSTANCE/"* $MIRROR_OUTPUT_DIR
rmdir "$MIRROR_OUTPUT_DIR/$LEX_INSTANCE"
popd

# Convert all hrefs and actions to use .html suffixes (none are present in the
#  dynamic site, so we can assume that this is safe to execute here.
# Don't try to add a .html to hrefs to the root director
# We use gnu sed here so we have access to the -i argument
find $MIRROR_OUTPUT_DIR -type f | \
	xargs gsed -i 's/href="\(\/[a-z][a-z/]*\)">/href="\1.html">/'
find $MIRROR_OUTPUT_DIR -type f | \
	xargs gsed -i 's/action="\(\/[a-z][a-z/]*\)"/action="\1.html"/'

# Convert map source json so that languages have a correct link
gsed -i 's/url: "\(language\/iso\/[a-z][a-z][a-z]\)"/url: "\1.html"/' $MIRROR_OUTPUT_DIR/map.html

# Adjust hrefs, action and src elements to be prefixed with the deployment
#  prefix (if one is used). Note that we only attempt to prefix with the
#  deployment prefix if there is a leading slash. As all URLs are absolute
#  this will give correct results and prevent external addresses e.g. http://
#  from incorrectly being prefixed with the deployment prefix
# Also adjust d3 json calls
if [ -n "$DEPLOYMENT_PREFIX" ]; then
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/href="\//href="\'$DEPLOYMENT_PREFIX'\//'
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/src="\//src="\'$DEPLOYMENT_PREFIX'\//'
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/action="\//action="\'$DEPLOYMENT_PREFIX'\//'
	find $MIRROR_OUTPUT_DIR -type f -name "*.html" | \
		xargs gsed -i 's/d3\.json("\//d3.json("\'$DEPLOYMENT_PREFIX'\//'
fi

# Show version and link to source
current_git_commit=$(git log -n1 --abbrev-commit --format=%h)
find $MIRROR_OUTPUT_DIR -type f | \
	xargs gsed -i "s/>######</>$current_git_commit</"


# Copy libraries
mkdir $LIBRARY_OUTPUT_DIR
pushd $STATIC_ASSET_BASE
cp -R $STATIC_ASSET_DIRNAME $MIRROR_OUTPUT_DIR
popd

pkill -f gunicorn

echo ""
echo "\nTo sync to external site, run: rsync -av ${MIRROR_OUTPUT_DIR}/ language-explorer.wordspeak.org:/var/www/htdocs/language-explorer.wordspeak.org"
