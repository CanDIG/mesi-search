#!/usr/bin/env python

"""Executable to run the app.

After you have configured your Python environment:

`./bin/run.py`
"""
from mesi_search import main

app = main.APP
app.config.from_object("mesi_search.settings")

if __name__ == '__main__':
    app.run()
