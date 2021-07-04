# About
This repository contains the codebase of my DBMS project named **Mini SQL Engine**.
Mini SQL Engine is written in Python and can parse and execute a subset of DML queries given using the command-line interface on data stored as CSV files. Please Read ```problem_description.pdf``` for more details.  

 Following cases of query processing are handled as of now.
- Blank column entries while entering data
- Single and double quoted values in CSV files
- Multiple AND/OR queries, including nested ones
- Operators handled in column comparison: `=, !=, >, <, <=, >=`
- Aggregate functions: `distinct, sum, min, max, avg.`
- Pretty Table output
- Summary of successful query
- Table aliasing

## Requirements
- Python 2.7 
- SQL Parse (```pip install sqlparse```)
- Pretty Table (```pip install prettytable```)

## Files
- ```mini_sql.py```: Main File
- ```sample_data```: It contains two sample data inside folders ```A``` and ```B``` for testing purpose.
- ```instructions.md```: Instructions to run sql query
- ```metadata.txt```: Contains metadata: table and column names
- ```table1.csv```: It contains data of table named "table1"
  
## NOTE:
1. Column name should not start with number but can contain a table name. 
2. The case of the DML language (query) does not matter.
4. When selection from multiple tables is made, the user will expect to give an equijoin condition; otherwise, it would perform cross-join and output the result accordingly.
5. In case of multiple AND/OR, the conditions must be properly enclosed within ```()```.
