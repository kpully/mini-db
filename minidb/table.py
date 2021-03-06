import operator
import numpy as np
from minidb.index import Index
from minidb.utils import Utils as utils


# noinspection PyPep8Naming
class Table:

    def __init__(self, name, columns):
        self.name = name
        self.num_columns = len(columns)
        self.num_rows = 0
        self.indexes = {}
        self.header = np.array([columns])
        self.rows = np.empty([0, self.num_columns])
        self.col_names = {}
        self.col_dtypes = {}
        for idx, col in enumerate(columns):
            self.col_names[col] = idx

    def is_col_numeric(self,idx):
        if self.__is_col_int(idx) or self.__is_col_float(idx):
            return True
        else:
            return False

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
        if self.__is_col_int(idx):
            to_return = self.rows[:, idx].astype(int)
            return to_return
        elif self.__is_col_float(idx):
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

    def __get_max_col_width(self):
        col_width = 1;
        for col_idx, dtype in self.col_dtypes.items():
            if dtype:
                w = len(max(self.rows[:, col_idx], key=len))
                if col_width < w:
                    col_width = w
        return col_width+2

    def copy(self, out_table_name):
        """create a "deep" copy of the input table
        :return: copied table
        """
        out_table = Table(out_table_name, self.col_names.keys())
        out_table.rows = self.rows
        out_table.num_rows = self.num_rows
        out_table.indexes = self.indexes
        out_table.header = self.header
        out_table.col_names = self.col_names
        out_table.col_dtypes = self.col_dtypes
        out_table.num_columns = self.num_columns
        return out_table

    def set_data(self, rows):
        """set rows, length of table, and data types for columns
        :param rows: np array of table data
        :return: None
        """
        self.rows = np.array(rows)
        self.num_rows = len(rows)
        if self.num_rows > 0:
            self.set_dtypes

    def set_dtypes(self):
        for col in list(self.col_names.keys()):
            idx = self.__get_column_idx(col)
            if self.__is_col_int(idx):
                self.col_dtypes[idx] = 1
            elif self.__is_col_float(idx):
                # set to 0 so condition can be checked as a bool
                self.col_dtypes[idx] = 0
            else:
                self.col_dtypes[idx] = 2

    def insert_row(self, new_row):
        self.rows = np.concatenate((self.rows, new_row))
        self.__auto_increment()

    def print(self, f=None, num_rows=None):
        """ print contents of the table
        :param f: file to print to. Prints to stdout if None
        :param num_rows: num of rows to print
        :return: None
        """
        self.print_columns(f)
        if num_rows is None:
            num_rows = self.num_rows
        for i in range(0, num_rows):
            for idx, value in enumerate(self.rows[i]):
                if idx != 0:
                    print(" | ", end='', file=f)
                print(value, end='', file=f)
            print("", file=f)

    def print_columns(self, f=None):
        """ print column names (separated by |)
        :param f: file to print to. Prints to stdout if None
        :return: None
        """
        print("")
        for idx, name in enumerate(self.col_names):
            if idx != 0:
                print(" | ", end='', file=f)
            print(name, end='', file=f)
        print("", file=f)

    def print_formatted(self, f=None, *args,**kwargs):
        """ print contents of the table
        :param f: file to print to. Prints to stdout if None
        :return: None
        """
        if self.num_rows > 0:
            self.set_dtypes()
        col_width = self.__get_max_col_width()
        # print header
        self.print_columns_formatted(col_width, f)
        if "num_rows" in kwargs:
            num_rows = kwargs["num_rows"]
        else:
            num_rows = self.num_rows
        # print table rows (separated by |)
        for i in range(0, num_rows):
            for idx, value in enumerate(self.rows[i]):
                if idx != 0:
                    print("", end='', file=f)
                print(str(value).ljust(col_width), end='', file=f)
            print("")

    def print_columns_formatted(self, col_width, f=None):
        """ print column names (separated by |)
        :param col_width: width of column
        :param f: file to print to. Prints to stdout if None
        :return: None
        """
        for idx, name in enumerate(self.col_names):
            if idx != 0:
                print("", end='', file=f)
            print(name.ljust(col_width), end='', file=f)
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

    def sort(self, result_table_name, columns):
        """sort table in ascending order on given column(s)
        :param result_table_name: name of table to output
        :param columns: ordered list of columns to sort on
        :return: None if column does not exist or sorted result table
        """
        result_table = Table(result_table_name, self.col_names)
        if (self.num_rows)>0:
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
            result_table.rows = sorted_rows
            result_table.num_rows = len(sorted_rows)
        else:
            result_table.num_rows=0
        return result_table

    def select(self, criteria):
    # perform select. select subset of rows and return resulting table
        for i in range(0, criteria.num_conditions):
            idx = self.__get_column_idx(criteria.conditions[i][0])
            if idx is None:
                print("column %s is not present in table %s" % (criteria.conditions[i][0], self.name))
                return False

            # get comparator (>, =, !=, etc.)
            comparator = utils.OPERATORS[criteria.comparators[i]]
            # get value on right side of comparator
            val = criteria.conditions[i][1]

            if criteria.arithops[i] is None:
                if utils.NUMERIC[comparator]:
                    c_new = comparator(self.rows[:, idx].astype(float), int(val))
                else:
                    c_new = comparator(self.rows[:, idx], val)
            else:
                arithop = utils.OPERATORS[criteria.arithops[i]]
                arithm = arithop(self.rows[:, idx].astype(float), float(criteria.conditions[i][2]))
                c_new = comparator(arithm, float(val))

            if i - 1 < 0:
                c = c_new
            else:
                logic_operator = utils.OPERATORS[criteria.logic_operators[i-1]]
                c = logic_operator(c_new, c)
        
        return self.rows[np.where(c)]

    def avg(self, out_table_name, column):
        # will average have multiple columns?
        result_table = Table(out_table_name, ["avg_"+column])
        idx = self.__get_column_idx(column)
        avg = np.mean(self.rows[:, idx].astype(float))
        avg = "{:.4f}".format(avg)
        result_table.insert_row([[avg]])
        return result_table

    def sum(self, out_table_name, column):
        # will average have multiple columns?
        result_table = Table(out_table_name, ["sum_"+column])
        idx = self.__get_column_idx(column)
        s = np.sum(self.rows[:, idx].astype(float))
        s = "{:.4f}".format(s)
        result_table.insert_row([[s]])
        return result_table

    def count(self, out_table_name):
        result_table = Table(out_table_name, ["count"])
        result_table.insert_row([[self.__get_length()]])
        return result_table

    def group(self, columns):
        projection = self.projection("projection", columns)
        keys, indices = np.unique(projection.rows, axis=0, return_inverse=True)
        # print(keys)
        groups = [[] for i in range(len(keys))]
        for i, k in enumerate(indices):
            groups[k].append(self.rows[i])
        groups = [np.array(x) for x in groups]
        return keys, groups

    def avggroup(self, out_table_name, avg_column, groupby_columns):
        result_table = Table(out_table_name, ["avg_"+avg_column] + groupby_columns)
        avg_idx = self.__get_column_idx(avg_column)
        keys, groups = self.group(groupby_columns)
        for i in range(0,len(groups)):
            s = np.mean(groups[i][:, avg_idx].astype(float))
            new_row = np.insert(keys[i], 0, "{:.4f}".format(s))
            result_table.insert_row([new_row])
        return result_table

    def sumgroup(self, out_table_name, sum_column, groupby_columns):
        result_table = Table(out_table_name, ["sum_" + sum_column] + groupby_columns)
        sum_idx = self.__get_column_idx(sum_column)
        keys, groups = self.group(groupby_columns)
        for i in range(0, len(groups)):
            if self.__is_col_int(sum_idx):
                s = np.sum(groups[i][:, sum_idx].astype(int))
            else:
                s = np.sum(groups[i][:, sum_idx].astype(float))
            new_row = np.insert(keys[i], 0, s)
            result_table.insert_row([new_row])
        return result_table

    def countgroup(self, out_table_name, count_column, groupby_columns):
        result_table = Table(out_table_name, ["count_" + count_column] + groupby_columns)
        count_idx = self.__get_column_idx(count_column)
        keys, groups = self.group(groupby_columns)
        for i in range(0, len(groups)):
            s = len(groups[i])
            new_row = np.insert(keys[i], 0, s)
            result_table.insert_row([new_row])
        return result_table

    def movavg(self, out_table_name, column, n):
        result_table = Table(out_table_name, list(self.col_names.keys()) + ["mov_avg"])
        weights = np.ones(n)
        c = self.rows[:, self.__get_column_idx(column)].astype(float)
        c = np.concatenate((np.zeros(n - 1), c), axis=None)
        o = np.concatenate((np.zeros(n - 1), np.ones(len(c))))
        sum_vec = np.convolve(c, weights, 'valid')
        div_vec = np.convolve(o, weights, 'valid')
        avg_vec = [x/y for x, y in zip(sum_vec, div_vec)]

        avg_vec = np.vstack(avg_vec)
        new_rows = np.hstack((self.rows,avg_vec))
        result_table.rows = new_rows
        result_table.num_rows = len(avg_vec)
        return result_table

    def movsum(self, out_table_name, column, n):
        result_table = Table(out_table_name, list(self.col_names.keys()) + ["mov_sum"])
        weights = np.ones(n)
        c = self.rows[:, self.__get_column_idx(column)].astype(float)
        c = np.concatenate((np.zeros(n - 1), c), axis=None)
        sum_vec = np.convolve(c, weights, 'valid')

        sum_vec = np.vstack(sum_vec)
        new_rows = np.hstack((self.rows,sum_vec))
        result_table.rows = new_rows
        result_table.num_rows = len(sum_vec)
        return result_table

    def btree_index(self, column):
        index = Index(self, self.__get_column_idx(column), "Btree")
        # index.print()
        self.indexes[column] = index

    def hash_index(self, column):
        index = Index(self, self.__get_column_idx(column), "Hash")
        # index.print()
        self.indexes[column] = index

    def apply_hash_transformation(self, column, constant, arithop_):
        arithop = utils.OPERATORS[arithop_]
        transformed_index = Index(self, self.__get_column_idx(column), "Hash_Transform", (arithop,constant))        
        self.indexes[column + "_tr"] = transformed_index

    def index_list(self):
        for key, idx in self.indexes.items():
            print("%-15s %-15s %-15s" % (self.name, key, idx.type))
