# Mini-SQL
A SQL engine written in python capable of parsing and executing simple and medium level (complexity) queries.
 _NOTE_: 1. Column name should not start with number and can contain a table name.
2. The case of the DML language (query) does not matter.
3. Consider 'CSE441_ DATABASE SYSTEMS ASSIGNMENT 1.pdf' for more details about the DML language.
4. When selection from multiple tables is made, then user will expect to give a equijoin condition. Else it would perform cross-join and output the result accordingly.
5. In case of multiple AND/OR, the conditions will be properly enclosed within parentheses.
<br/>
Handles the following cases of query processing:
- Blank column entries while entering data from data_file.
- Handles single and double quotted values
- Multiple AND or OR queries, including nested ones.
- Handling operators like `=, !=, >, <, <=, >=` in column comparison.
- Aggregate function like, (distinct, sum, min, max, avg)
- Pretty Table output
- Summary of successful query
- Handle table alaising
