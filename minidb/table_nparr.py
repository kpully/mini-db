from minidb.index import Index
from BTrees.OOBTree import OOBTree
import numpy as np
import os
import operator


"""
Changelog:
1. self.columns not being used. removed.
2. changed self.size to self.num_rows. more readable.
3. made __auto_increment as a way to update self.num_rows
4. made get_length private. no need for this to be accessible outside 
5. adding movingavg() to table 

new:
6. created self.index, a dict that holds index for each column (if added).
[Will each column have only a max of 1 index? Or should self.indexes hold a list of indexes?]
7. added btree_index() and hash_index() for creating indexes of each type respectively


To-do
1. using index (if present) for each operation.

"""

# should this be put in a "constants" class or in the utils class?
# sam: If these are the only constants we have and they are used here only, then it is
#      not necessary to create new class
OPERATORS = {
    "<": operator.lt, ">": operator.gt, "=": operator.eq, "!=": operator.ne,
    "≥":   operator.ge, "≤": operator.le, "and": operator.and_, "or": operator.or_
}

NUMERIC = {
    operator.lt: True, operator.gt: True, operator.eq: False, operator.ne: False,
    operator.ge: True, operator.le: True, operator.and_: False, operator.or_: False
}


# noinspection PyPep8Naming
class Table:

    def __init__(self, name, columns):
        self.name = name
        self.num_columns = len(columns)
        self.num_rows = 0
        self.index = {}
        self.header = np.array([columns])
        self.rows = np.empty([0, self.num_columns])
        self.col_names = {}
        for idx, col in enumerate(columns):
            self.col_names[col] = idx

    def __is_col_int(self, idx):
        try:
            int(self.rows[0][idx])
            return True
        except ValueError:
            return False

    def __is_col_float(self, idx):
        try:
            float(self.rows[0][idx])
            return True
        except ValueError:
            return False

    def __get_col_with_dtype(self, idx):
        if (self.__is_col_int(idx)):
            return self.rows[:, idx].astype(int)
        elif (self.__is_col_float(idx)):
            return self.rows[:, idx].astype(float)
        else:  # return as string
            return self.rows[:, idx]

    def __get_length(self):
        return len(self.rows)

    def __auto_increment(self):
        self.num_rows += 1
        return self.num_rows

    def __get_column_idx(self, col_name):
        if col_name in self.col_names:
            return self.col_names[col_name]
        else:
            return None

    def get_dimensions(self):
        return self.rows.shape

    def insert_row(self, new_row):
        self.rows = np.concatenate((self.rows, new_row))
        self.__auto_increment()

    def print(self, f=None):
        """ print contents of the table
        :param f: file to print to. Prints to stdout if None
        :return: None
        """
        # print header
        self.print_columns(f)
        # print table rows (separated by |)
        for i in range(0, self.num_rows):
            for idx, value in enumerate(self.rows[i]):
                if idx != 0:
                    print(" | ", end='', file=f)
                print(value, end='', file=f)
            print("")

    def print_columns(self, f=None):
        """ print column names (separated by |)
        :param f: file to print to. Prints to stdout if None
        :return: None
        """
        for idx, name in enumerate(self.col_names):
            if idx != 0:
                print(" | ", end='', file=f)
            print(name, end='', file=f)
        print("")

    def projection(self, name, columns):
        # if given list of column names is beyond this table
        if len(columns) > self.num_columns:
            return None

        idx = []
        projected_table = Table(name, columns)

        # create a list of indexes of given columns
        for col in columns:
            if col not in self.col_names:
                print("Invalid command. Column not present in table")
                return None
            idx.append(self.__get_column_idx(col))

        # insert a row, but only include columns with index in `idx`
        for row in self.rows:
            new_row = []
            for i in idx:
                new_row.append(row[i])
            projected_table.insert_row(np.array([new_row]))

        return projected_table

    def sort(self, result_table_name,columns):
        result_table=Table(result_table_name,self.col_names)
        idx = []
        for col in columns:
            if col not in self.col_names:
                print("Invalid command. Column not present in table")
                return None
            else:
                i = self.__get_column_idx(col)
                idx.insert(0, self.__get_col_with_dtype(i))
        
        order = np.lexsort(idx)
        sorted_rows = self.rows[order]
        result_table.rows=sorted_rows
        result_table.num_rows=len(sorted_rows)
        return result_table

    def select_join(self, criteria):
        for i in range(0, criteria.num_conditions):
            idx1 = self.__get_column_idx(criteria.conditions[i][0])
            idx2 = self.__get_column_idx(criteria.conditions[i][1])
            if idx1 is None:
                print("column %s is not present in table %s" % (criteria.conditions[i][0], self.name))
                return False
            if idx2 is None:
                print("column %s is not present in table %s" % (criteria.conditions[i][1], self.name))
                return False

            comparator = OPERATORS[criteria.comparators[i]]
            c_new = comparator(self.rows[:, idx1], self.rows[:, idx2])

            if i - 1 < 0:
                c = c_new
            else:
                logic_operator = OPERATORS[criteria.logic_operators[i-1]]
                c = logic_operator(c_new, c)

            return self.rows[np.where(c)]

    def select(self, criteria):
        # perform select. select subset of rows and return resulting table
        for i in range(0, criteria.num_conditions):
            idx = self.__get_column_idx(criteria.conditions[i][0])
            if idx is None:
                print("column %s is not present in table %s" % (criteria.conditions[i][0], self.name))
                return False
            
            comparator = OPERATORS[criteria.comparators[i]]
            val = criteria.conditions[i][1]

            if NUMERIC[comparator]:
                c_new = comparator(self.rows[:, idx].astype(int), int(val))
            else:
                c_new = comparator(self.rows[:, idx], val)

            if i - 1 < 0:
                c = c_new
            else:
                logic_operator = OPERATORS[criteria.logic_operators[i-1]]
                c = logic_operator(c_new, c)
        
        return self.rows[np.where(c)]

    def avg(self,out_table_name,column):
        # will average have multiple columns?
        result_table=Table(out_table_name,column)
        idx = self.__get_column_idx(column[0])
        avg = np.mean(self.rows[:,idx].astype(float))
        result_table.insert_row([[avg]])
        return result_table

    def group(self,columns):
        projection = self.projection("projection",columns)
        keys,indices=np.unique(projection.rows,axis=0,return_inverse=True)
        # print(keys)
        groups = [[] for i in range(len(keys))]
        for i,k in enumerate(indices):
            groups[k].append(self.rows[i])
        groups = [np.array(x) for x in groups]
        return keys,groups

    def avggroup(self,out_table_name,avg_column,groupby_columns):
        result_table=Table(out_table_name,[avg_column]+groupby_columns)
        avg_idx=self.__get_column_idx(avg_column)
        keys,groups=self.group(groupby_columns)
        for i in range(0,len(groups)):
            s=np.mean(groups[i][:,avg_idx].astype(float))
            new_row=np.insert(keys[i],0,s)
            result_table.insert_row([new_row])
        return result_table

    def sumgroup(self,out_table_name,sum_column,groupby_columns):
        result_table=Table(out_table_name,["sum_"+sum_column]+groupby_columns)
        sum_idx=self.__get_column_idx(sum_column)
        keys,groups=self.group(groupby_columns)
        for i in range(0,len(groups)):
            if (self.__is_col_int(sum_idx)):
                s = np.sum(groups[i][:,sum_idx].astype(int))
            else:
                s = np.sum(groups[i][:,sum_idx].astype(float))
            new_row = np.insert(keys[i],0,s)
            result_table.insert_row([new_row])

        return result_table

    def movavg(self, out_table_name, column, n):
        result_table = Table(out_table_name, column)
        weights = np.ones(n)
        c = self.rows[:, self.__get_column_idx(column)].astype(float)
        c = np.concatenate((np.zeros(n - 1), c), axis=None)
        o = np.concatenate((np.zeros(n - 1), np.ones(len(c))))
        sum_vec = np.convolve(c, weights, 'valid')
        div_vec = np.convolve(o, weights, 'valid')
        avg_vec = [x/y for x, y in zip(sum_vec, div_vec)]
        # print(weights, c, o, sum_vec, div_vec, avg_vec)
        for num in avg_vec:
            result_table.insert_row([num])
        return result_table

    def movsum(self, out_table_name, column, n):
        result_table = Table(out_table_name, column)
        weights = np.ones(n)
        c = self.rows[:, self.__get_column_idx(column)].astype(float)
        c = np.concatenate((np.zeros(n - 1), c), axis=None)
        avg_vec = np.convolve(c, weights, 'valid')
        # print(avg_vec)
        for num in avg_vec:
            result_table.insert_row([num])
        return result_table

    def btree_index(self, column):
        index = Index(self, self.__get_column_idx(column), "Btree")
        index.print()
        self.index[column] = index

    def hash_index(self, column):
        index = Index(self, self.__get_column_idx(column), "Hash")
        index.print()
        self.index[column] = index

    def index_list(self):
        for key, idx in self.index.items():
            print("%-15s %-15s %-15s" % (self.name, key, idx.type))
