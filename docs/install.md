This is mostly my notes to help with getting this going after a period of absence

# Install/Setup

1. create virtualenv for this project, language_explorer
2. ``source ~/.virtualenvs/language_explorer/bin/activate``
3. ``pip install -r requirements.txt --allow-external PyX``
4. **Staging/Prod:** ``pip install ~/language_explorer-0.1.0.tar.gz``
5. **Staging:** ``export LANGUAGE_EXPLORER_DEPLOYMENT=staging``
6. **Development:** ``export LANGUAGE_EXPLORER_DEPLOYMENT=dev``
7. ``psql -c "CREATE DATABASE language_explorer"``
8. Run through the ``DataSources.md`` file in this directory to obtain and setup data sources
10. Load all the data sources: ``cd language_explorer; python -m language_explorer.loader``
11. Run the unit/system tests to make sure everything is setup properly: ``python setup.py test``     **2 failures with 2015 JP Harvest data: test_all_iso_keys, test_same_name_different_iso**

# Running
Assuming the working directory is the root of the checkout

## Development

``PYTHONPATH=. python -m language_explorer`` 

setting PYTHONPATH is yuk, but effective. View at <http://localhost:5000> (fabric default)

## Staging
``~/.virtualenvs/language_explorer/bin/gunicorn -b 127.0.0.1 language_explorer:app``

View at <http://localhost:8000> (gunicorn default)

# Migrating Data from a working instance

1. ``make_data_bundle.sh`` on the machine with the data set
2. copy data bundle to target machine and unpack
3. on the target machine run ``load_data_bundle.sh`` that was unpacked in the previous step

# Building and Installing

1. ``cd language_explorer/language_explorer``
2. ``python setup.py sdist``
2. copy tar.gz sdist file to target machine, and unpack