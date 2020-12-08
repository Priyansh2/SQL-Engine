# About
This repository contains code resource of my DBMS project named **Mini SQL Engine**.
Mini SQL Engine is written in Python and can parse and execute SQL queries (given using command-line interface) on data stored as CSV files. ```sqlparse``` library is used to format a given query which then parsed and executed by the engine. Read ```problem_description.pdf``` for details.  

 Following cases of query processing are handled as of now.
- Blank column entries while entering data
- Single and double quotted values in CSV files
- Multiple AND/OR queries, including nested ones
- Operators handled in column comparison: `=, !=, >, <, <=, >=`
- Aggregate functions: `distinct, sum, min, max, avg`
- Pretty Table output
- Summary of successful query
- Table alaising

## Requirements
- Python 2.7 
- SQL Parse (```pip install sqlparse```)
- Pretty Table (```pip install prettytable```)

## Files
- ```mini_sql.py```: Intensively documented main file 
- ```sample_data```: It holds two sample data inside folders ```A``` and ```B``` for experimentation
- ```instructions.md```: Instructions to run sql query
- ```metadata.txt```: Metadata file, it contains table and column names
- ```table1.csv```: It holds data of table named "table1"
  
## NOTE:
1. Column name should not start with number but can contain a table name. 
2. The case of the DML language (query) does not matter.
4. When selection from multiple tables is made, then user will expect to give a equijoin condition else, it would perform cross-join and output the result accordingly.
5. In case of multiple AND/OR, the conditions will be properly enclosed within ```()```.
