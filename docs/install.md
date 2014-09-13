
1. run ansible/vagrant
2. python setup.py sdist
3. copy tar.gz sdist file to vm, and unpack
4. make_data_bundle.sh
5. copy data bundle to vm, and unpack
6. load_data_bundle.sh
7. source ~/.virtualenvs/language_explorer/bin/activate
8. pip install -r requirements.txt --allow-external PyX
9. pip install ~/language_explorer-0.1.0.tar.gz
9. export LANGUAGE_EXPLORER_DEPLOYMENT=staging
10. python -m language_explorer.loader
11. python setup.py test
12. python -m language_explorer   ^C
13. gunicorn -b 127.0.0.1:4000 language_explorer:app
