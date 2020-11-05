#!/usr/bin/env python
import os
import sys
import re
import collections
import sqlparse
import prettytable
import copy

main_script_path = os.path.dirname(os.path.realpath(__file__))
data_path=main_script_path
schema={} ##dictionary of tuples where each tuple belongs to a table which conatins all its column names
dataset=collections.defaultdict(list) ##dictionary in which table is key and its value is a list which contains each of its row as dict
AGGREGATE_FUNCTIONS=("avg", "max", "min", "sum")
CONDITIONAL_TUPLE=("AND", "OR", "(", ")")
OPERATOR_TUPLE=("=", ">", "<", "!=", "<=", ">=")

class Exceptions(Exception):
    pass


def quotes_removal(s): ## to remove "" or '' from values in table.
    ### return quotes(single or double) free value (integer or variable/column name)
    s = s.strip()
    while len(s) > 1 and (s[0]=='\"' or s[0]=='\'') and s[0]==s[-1]:
        s = s[1:-1] ## copying original str say,"abcxyz" or 'abcxyz' to abcxyz
    return s

def generate_schema_and_load_data(filename):
##Generate the table structure using database schema
##here filename is "metadata.txt"
    with open(os.path.join(data_path,filename), "r") as f:
        table_found=-1
        for row in f.readlines():
            row=quotes_removal(row) ## to remove "" or '' from each row of metadata.txt
            #print len(row)
            if row=="<begin_table>":
                table_found=0
            elif row=="<end_table>":
                table_found=-1
            else:
                if table_found==0:
                    schema[row]=()
                    #print schema[row]
                    table_found=row #table name
                    #print table_found
                else: ##Assuming a column name is a capital english alphabet
                    schema[table_found]+=(table_found+"."+row,) ##only one element in tuple
                    #print schema[table_found]
    f.close()
    #print "Database Schema Created Using Metadata"

    files=[] #contains table filenames
    for filename in os.listdir(data_path):
        temp=[]
        temp=filename.split(".")
        if len(temp)==2:
            if temp[1]=="csv":
                if temp[0] in schema.keys():
                    table_filename=temp[0]
                    for z in range(1,len(temp)):
                        table_filename+="."+temp[z]
                    files.append(table_filename)

    ## Loading data from all the files
    #print "Data is loading from each table files"
    for filename in files:
        #print "Data loaded from "+str(filename)
        with open(os.path.join(data_path,filename),"r") as f:
            for row in f.readlines():
                split_row=row.split(",")
                tablename=filename.split(".")[0]
                #print schema[tablename]
                #print split_row
                #print zip(schema[tablename],split_row)
                each_row_info=zip(schema[tablename],split_row)
                values=[]
                columns=[]
                for i in each_row_info:
                    j=list(i)
                    if len(quotes_removal(j[1]))>0: ###if value is present
                        values.append(int(quotes_removal(j[1])))
                        columns.append(j[0])
                    else: ## if value is missing
                        values.append(0) ##putting zero in the empty space
                        columns.append(j[0])
                temp_dict={}
                #print values
                #print columns
                for x in range(0,len(columns)):
                    temp_dict[columns[x]]=values[x]
                #print temp_dict
                dataset[tablename].append(temp_dict)
        f.close()


def adding_table_alias_in_schema_and_dataset(table_name,alias_name):
    ###Here table alias (as mentioned in query) after validation, put in main data and schema
    ###This process will repeat everytime whenever a user gives input query in which he/she is using the aliases
    global dataset, schema
    if alias_name in schema.keys():
        raise MyException('Table already exists: Cannot create alias')

    temp=[]
    for col in schema[table_name]:
        temp1=alias_name+"."+col.split(".")[1] ##"table_alias.col"
        #print temp1
        temp.append(temp1)
    schema[alias_name]=tuple(temp) ##adding table_alias in schema
    #print schema[alias_name]
    dataset[alias_name]=copy.deepcopy(dataset[table_name])
    #print dataset[alias_name]
    for row in dataset[alias_name]: ##each row is the dict and also row of table
        for (key,val) in row.items():
            temp1=alias_name+"."+key.split(".")[1]
            row[temp1]=copy.deepcopy(row[key]) ## adding table alias in dataset
            del row[key]
    #print dataset[alias_name]

def handling_colname_with_tablename(column_name,tables):
    ###Converts the column names from "col" to "table.col" and returns the same
    ###eg: A --> <table>.A (if alias not present) else <table_alias>.A
    #if "*" in column_name:
        #print column_name
    #print column_name
    #print tables
    if "." in column_name:   # No need to change as the name is already generic
        return column_name
    found=[]
    for table in tables:
        temp=table+"."+column_name
        if temp in schema[table]:
            found.append(table)
    if len(found)==0:
        #print "yoyo"
        raise Exceptions('Could not find the column in table')
    elif len(found)>1:
        raise Exceptions('Presence of conflicting columns')
    return found[0]+"."+column_name

def get_aggregate_func(col,tables):
    ##Returns the aggregate func used in query with the column name in generic form
    ## e.g:- max(A) or Max(A) or MAX(a) ----> <table_name>.A or <table_alias>.A, max
    ### AGGREGATE_FUNCTIONS contains all functions name in lower case form
    ##Returns: column_name, function_name
    ### NOTE:- can never take column name as <tablename>.col
    #print col
    #print tables
    if "." not in col:
        #print col
        count=[]
        function=None
        for func in AGGREGATE_FUNCTIONS:
            reg=re.compile(r'(%s)\(([a-zA-Z]+)\)' %(func),re.IGNORECASE)
            #print col
            col2=re.sub(reg,r'\2',col) ##replace func(col) with 2nd matched group i.e with column name
            function=func
            if col!=col2: ##this will become true if aggregate func do exist in query
                break
        if col==col2: ##this condition is true only if cloumn name is not present in any of mentioned table in query
            #print "lol"
            return col,None

        col_name = handling_colname_with_tablename(col2,tables)
    else:
        #print col
        count=[]
        function=None
        for func in AGGREGATE_FUNCTIONS:
            reg=re.compile(r'(%s)\(([a-zA-Z0-9]+\.[a-zA-Z]+)\)' %(func),re.IGNORECASE)
            #print col
            col2=re.sub(reg,r'\2',col) ##replace func(col) with 2nd matched group i.e with column name
            function=func
            if col!=col2: ##this will become true if aggregate func do exist in query
                break
        if col==col2: ##this condition is true only if cloumn name is not present in any of mentioned table in query
            #print "lol"
            return col,None

        col_name = handling_colname_with_tablename(col2,tables)
    return col_name,function

def display_result(distinct_flag,new_schema,aggregate_functions_map,columns,final_dataset):
    ### If aggregrate function is present in query then processing it and then
    ### projects the columns using prettytable module in python which pop out data
    ### in tabular form similar to sql output
    ### final_dataset is modified in the process_aggregate_function(). This modified
    ### final_dataset is what we are going to display in tabular form
    ### Returns: final_dataset
    ###Assumptions made:-
    ### 1. aggregate func should present only once with SELECT clause and does not present with WHERE clause.
    ### 2. combination of aggregate func. are not allowed in sql query
    field_names=[] ##contains all columns names in genric form which are present in the sql query
    if "*" in columns:
        field_names=list(new_schema)
    else: ## if "." is present in column
        if len(aggregate_functions_map)>=1: ##presence of aggregate function
            if len(aggregate_functions_map)>1: ## if select clause have more than 1 aggregate_func (same or different)
                raise Exceptions('More than one aggregrate functions are present')
            (agg_col,agg_func)=aggregate_functions_map[0] ##Here agg_col is in generic form
            field_names,final_dataset=aggregate_func_computation(agg_col,agg_func,final_dataset,new_schema)
        else: ## absence of aggregate function
            for col in columns:
                if col!="*":
                    field_names.append(col)

    x=prettytable.PrettyTable(field_names)
    distinct_rows=[]
    all_rows=[]
    for row in final_dataset:
        temp=[]
        for field in x.field_names:
            temp.append(row[field])
        all_rows.append(temp)
        if temp not in distinct_rows:
            distinct_rows.append(temp)
    #print all_rows
    #print distinct_rows
    #print distinct_flag
    if distinct_flag!=1: ##if 'distinct' not present in 'select' clause
        for row in all_rows:
            x.add_row(row)
    else:
        for row in distinct_rows:
            x.add_row(row)
    print x



def aggregate_func_computation(agg_col,agg_func,final_dataset,new_schema):
    ##Computation is done as per different agg_func
    ##Returns: new_schema, processed_final_dataset
    #print new_schema
    new_col_name=agg_func+"("+agg_col+")"
    #print new_col_name
    #print agg_func
    #print agg_col
    #for row in final_dataset:
        #print row[agg_col]
    if agg_func=="sum":
        s=0
        for row in final_dataset:
            s+=row[agg_col]
        #s=str(s)
        final_dataset=[{new_col_name:s}]
        return [new_col_name],final_dataset

    elif agg_func=="avg":
        s=0
        for row in final_dataset:
            #print type(str(row[agg_col]))
            s+=row[agg_col]
        print len(final_dataset)
        avg=float(s)/len(final_dataset)
        avg="%.2f" %avg##two places of decimal
        #s=str(s)
        final_dataset=[{new_col_name:avg}]
        return [new_col_name],final_dataset

    elif agg_func=="max":
        temp=[]
        for row in final_dataset:
            temp.append(row[agg_col])
        maxi=max(temp)
        #s=str(s)
        final_dataset=[{new_col_name:maxi}]
        return [new_col_name],final_dataset

    elif agg_func=="min":
        temp=[]
        for row in final_dataset:
            temp.append(row[agg_col])
        mini=min(temp)
        final_dataset=[{new_col_name:mini}]
        return [new_col_name],final_dataset

    else:
        raise Exceptions('Processing of aggregrate functions failed')


def query_handling(query):
    ###returns:-  new_schema, columns (a list which contains all col names in generic form),
    ###           final_dataset(used to project columns), aggregate_functions_map (map colname with agg_func)
    #print query
    try:
        condition_process_flag=0
        stage=None ## SELECT , FROM , WHERE  --> stages of sql input_query
        columns=[] ##contains name of columns of tables which apper in query
        tables=[] ##contains name of tables which appear in query
        conditionals=[] ##contains expressions which involves some conditional operations
        aggregate_functions_map=[] ##of the format [(<table|table_alias>.col1, max) and so on]

        #parsing query deeply(parts wise)
        for parts in query.split("\n"):
            subparts=parts.split()
            if len(subparts)>=2:
                if subparts[0] in ("SELECT", "FROM", "WHERE"):
                    stage=subparts[0]

            if stage=="SELECT":
                #print subparts[0]
                ### symbol:- ',' if present in subpart of query then it will occur only at end
                if subparts[0]=="SELECT":
                    for element in subparts:
                        if str(element)=="DISTINCT":
                            distinct_flag=1
                            break
                        else:
                            distinct_flag=0
                comma_removed_subpart=subparts[-1].strip(",")
                #print comma_removed_subpart
                columns.append(quotes_removal(comma_removed_subpart))

            elif stage=="FROM":
                #print subparts[0]
                if subparts[0]=="FROM":
                    temp=subparts[1]
                    for z in range(2,len(subparts)):
                        temp+=" "+subparts[z]
                    table_info=temp.strip(",") ##table_info contains names of all tables
                    #print table_info
                    tables.append(quotes_removal(table_info))
                else:
                    temp=subparts[0]
                    for z in range(1,len(subparts)):
                        temp+=" "+subparts[z]
                    table_info=temp.strip(",")
                    #print table_info
                    tables.append(quotes_removal(table_info))

            elif stage=="WHERE":
                #print subparts[0]
                if subparts[0]=="WHERE":
                    temp=subparts[1]
                    for z in range(2,len(subparts)):
                        temp+=""+subparts[z]
                    conditionals.append(temp)
                else:
                    temp=subparts[0]
                    for z in range(1,len(subparts)):
                        temp+=" "+subparts[z]
                    conditionals.append(temp)

            else:
                raise Exceptions("Sql querry is not correct")

        ## STEP-0
        '''print "STEP-0"
        print tables
        print columns
        print conditionals'''
        ### Preserving the order by putting bracket around each conditional expression
        if conditionals:
            condition_process_flag=1
            temp=conditionals[0]
            for z in range(1,len(conditionals)):
                temp+=" "+conditionals[z]
            text=temp
            pattern=re.compile(r'(\(|\))') ##matches either '(' or ')'
            substituted_conditionals=re.sub(pattern,r' \1 ',text) ##replacing matching one sided parenthesis with same parenthesis with surrounding space
            conditionals=substituted_conditionals.split()
            #print conditionals
            pattern2=re.compile(r'(=|!=|>|<|<=|>=)') ##matches all the operators
            temp=[]
            for i in conditionals:
                if i not in CONDITIONAL_TUPLE:
                    text2=i
                    sub_cond=re.sub(pattern2,r' \1 ',text2) ## replaces matching operator with same operator with surround space
                    cond=tuple(sub_cond.split())
                else:
                    cond=i
                temp.append(cond)
            conditionals=temp
            #print conditionals


        ####Step-1
        '''print "STEP-1"
        print tables
        print columns
        print conditionals'''
        ##validation of table alias mentioned in sql query
        new_tables=[]
        for table in tables:
            if table not in schema.keys():
                table_list=table.split()
                #print len(table_list)
                #print table_list[0]
                #print table_list[1].lower()
                ## Handling table aliases
                if len(table_list)==3 and table_list[1].lower()=="as":
                    if table_list[0] in schema.keys():
                        #print "lol1"
                        adding_table_alias_in_schema_and_dataset(table_list[0],table_list[2]) ##table_list[2] is table alias
                        table=table_list[2]
                    else:
                        #print "lol2"
                        raise Exceptions('Could not find the table in database')
                else:
                    #print "lol3"
                    raise Exceptions('Could not find the table in database')
            #print "lol4"
            new_tables.append(table) ###inserting table alias as name of table (if alias is given) once the table is found in the data
        tables=new_tables ###if alias is present then tables are now with their alias
        ###Step-2
        '''print "STEP-2"
        print tables
        print columns
        print conditionals
        '''
        ## Check conflicting column names
        temp_flag=0
        new_columns=[]
        for col in columns:
            if col=="*":
                new_columns.append(col)
                temp_flag=1
            elif "." not in col: ###if column is present in genric form eg: <tablename>.col
                #print "lol2"
                count=[]## how many times a particular col is present in all tables appeared in query
                for table in tables:
                    temp=table+"."+col
                    if temp in schema[table]:
                        count.append(table)
                if len(count)>1: ##when columns mentioned in query are present in more than one tables then conflicting occurs
                    raise Exceptions('Presence of conflicting columns')
                elif len(count)==0: ##presence of aggregate func as column which not belongs to any table metioned in query
                    #print "lol5"
                    col,func=get_aggregate_func(col,tables)
                    #print "yoyo"
                    if not func: ##When column name does not appear in the table as mentioned in the input query
                        raise Exceptions('Could not find the column in table')
                    aggregate_functions_map.append((col,func))
                else:
                    col=count[0]+"."+col
            else:
                if len(col.split("."))==2:
                    count=[]
                    for table in tables:
                        temp=col
                        #print temp.split(".")[1]
                        #print temp
                        #print schema[table]
                        if temp in schema[table]:
                            count.append(table)
                    #print count
                    if len(count)>1:
                        #print "lol1"
                        raise Exceptions('Presence of conflicting columns')
                    elif len(count)==0:
                        #print "lol2"
                        col,func = get_aggregate_func(col,tables)
                        if not func:
                            raise Exceptions('Could not find the column in table')
                        aggregate_functions_map.append((col,func))

                    else:
                        #print "lol3"
                        col=col

                else:
                    print "Something is wrong"
                #print "lol4"
                #print col
            if temp_flag!=1:
                new_columns.append(col)
        columns=new_columns ##Adding all column name with table_name or table_alias. eg: <table>.col or <table_alias>.col
        ###Step-3
        '''print "STEP-3"
        print tables
        print columns
        print conditionals'''

        ## Selecting of schema in which all tables are their as per their alias or like <table>.col
        new_schema=()
        for tab in tables:
            new_schema+= schema[tab]

        #print schema
        #print new_schema

        ## Create master dataset (all possible combinations of rows of all tables:-
        ## cross product of sets for particular table which contains rows(dict) of that table)

        ### Let tables_set contain m tables where a table mi have ai ad bi rows and columns respectively for 1<=i<=m
        ### Since each row of a particular table is a dict. So for any row ai len(dict) is bi for ith table
        ### So new_dataset would contain (a1*a2*a3.....*am) elements.

        ### Considering each table as set Ai for ith table, which contains all rows of that table then new_dataset
        ### would be considered as cross product of all these sets i.e, (A1 X A2 X A3.... X Am). The purpose of
        ### forming such dataset is to evaluate the joining condition in sql input_query and processing aggregate func.

        new_dataset=[{}]
        for table in tables:
            #print len(dataset[table])
            dataset2=[]
            for x in dataset[table]:
                for y in new_dataset:
                    z={}
                    z.update(x)
                    z.update(y)
                    #print z
                    dataset2.append(z)
            new_dataset=dataset2
        #print len(new_dataset)
        #print dataset
        #print new_dataset

        ## Evaluation of where clause conditions
        ## Here we are going to evaluate our conditionals set which contains conditional expression involving some operators
        final_dataset=[]
        for row in new_dataset:
            new_cond=[]
            #print "lol"
            for condition in conditionals:
                #print "lol1"
                if condition in CONDITIONAL_TUPLE:
                    #print condition
                    new_cond.append(condition.lower())
                else:
                    #print condition
                    ## table_column can either be in one of two forms:- <table_name>.col or col
                    ## operator here are comparison operators like =,<,>,!= etc.
                    ## val here can be integer or <table_name>.col (which represents a value of column <col> of table <table_name>)

                    if len(list(condition))>3:
                        operator=list(condition)[1]+""+list(condition)[2]
                    elif len(list(condition))==3:
                        operator=list(condition)[1]
                    else:
                        print "Something is wrong"
                    table_column=list(condition)[0]
                    val=list(condition)[len(list(condition))-1]

                    #print table_column
                    #print operator
                    #print val
                    table_column=handling_colname_with_tablename(table_column,tables) ### converting to <table_name>.col form
                    try:
                        val=int(quotes_removal(val)) ### if it is an integer
                    except ValueError: ### else we have to generate the integer value
                        tab2=handling_colname_with_tablename(val,tables)
                        val=row[tab2]

                    if (operator=="=" and row[table_column]==val) or \
                       (operator==">" and row[table_column]>val) or \
                       (operator=="<" and row[table_column]<val) or \
                       (operator=="!=" and row[table_column]!=val) or \
                       (operator=="<=" and row[table_column]<=val) or \
                       (operator==">=" and row[table_column]>=val):
                        new_cond.append("True")
                    else:
                        if operator not in OPERATOR_TUPLE:
                            raise Exceptions('Presence of invalid operator')
                        new_cond.append("False")

            ## Evaluation of whole boolean expression
            #print new_cond
            #print "lol3"
            flag="True"
            if len(new_cond)>0:
                boolean_exp=new_cond[0]
                for z in range(1,len(new_cond)):
                    boolean_exp+=" "+new_cond[z]
                bool_val=str(eval(boolean_exp))
            else:
                bool_val="True"
            if bool_val==flag:
                final_dataset.append(row) ###Contains rows of tables after evaluating where conditions
        #print final_dataset
    except Exceptions as e:
        print "ERROR: "+e.args[0]

    return distinct_flag,new_schema,columns,final_dataset,aggregate_functions_map





if __name__ == "__main__":
    try:
        if len(sys.argv)==2:
            metadata_filename="metadata.txt"
            generate_schema_and_load_data(metadata_filename)
            input_query=sys.argv[1]
            #print input_query
            formatted_query=sqlparse.format(input_query,reindent=True,keyword_case='upper')
            #print formatted_query
            distinct_flag,new_schema,columns,final_dataset,aggregate_functions_map=query_handling(formatted_query)
            #print final_dataset
            display_result(distinct_flag,new_schema,aggregate_functions_map,columns,final_dataset)

        else:
            raise Exceptions('Insufficient no of arguments')
    except Exceptions as e:
        print "ERROR: "+e.args[0]

