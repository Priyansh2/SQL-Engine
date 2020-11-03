# Mini-SQL
A SQL engine written in python capable of parsing and executing simple and medium level (complexity) queries on data stored as CSV files. Read 'CSE441_ DATABASE SYSTEMS ASSIGNMENT 1.pdf' for details.  

 Following cases of query processing are handled as of now.
- Blank column entries while entering data
- Single and double quotted values
- Multiple AND/OR queries including nested ones
- Operators handled in column comparison: `=, !=, >, <, <=, >=`
- Aggregate functions: `distinct, sum, min, max, avg`
- Pretty Table output
- Summary of successful query
- Table alaising
 
 ## NOTE: 
1. Column name should not start with number and can contain a table name [TODO]
2. The case of the DML language (query) does not matter.
4. When selection from multiple tables is made, then user will expect to give a equijoin condition else, it would perform cross-join and output the result accordingly.
5. In case of multiple AND/OR, the conditions will be properly enclosed within parentheses.

