#!/bin/sh
pip install sqlparse
pip install prettytable
python mini_sql.py "$@"
