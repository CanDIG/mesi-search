# mesi-search

## Description

## Development

### Create virtualenv, activate, install requirements

```bash
python -m venv env
source ./env/bin/activate
pip install -e .
pip install -r requirements/dev.txt
```

### Run project

```bash 
python bin/run.py
```
or
```bash
./bin/run.py
```

### Run tests

The best usage is to just run `tox`.

```
tox
```

Alternatively, `pytest` can be invoked

```bash
pytest
```

Also, via `setup.py`

```bash
python setup.py test
```

## Deployment

### Create virtualenv, activate, install

```bash
python -m venv env
source ./env/bin/activate
pip install .
```

### Run using `gunicorn`

```bash
gunicorn --workers 2 --bind 0.0.0.0:5000 -k gevent run:app --chdir bin
```


## Note
This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
