# Installation

## Debian/ubuntu

```
apt-get install libcurl4-openssl-dev libpython3.5-dev
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Key file

You need to put the API key into a file called `~/.redcap-key`. You should
make this file unreadable by anyone other than the process that will be
fetching from redcap.

## Usage

### Options

```
usage: ExportAll.py [-h] [--all] ID [ID ...]

RedCap REST client

positional arguments:
  ID          a list of subject IDs to fetch metadata from

optional arguments:
  -h, --help  show this help message and exit
  --all       export all subject sessions even when marked as disabled
              (default: exclude disabled)

```

### Examples

```python
# fetch one subject, filter out disabled sessions
python ExportAll.py CC00111XX04

# fetch one subject, including disabled sessions
python ExportAll.py CC00111XX04 --all

# fetch multiple subjects, including disabled sessions
python ExportAll.py CC00111XX04 CC00668XX17 CC00713XX12 --all
```
