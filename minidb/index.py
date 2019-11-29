
from BTrees.OOBTree import OOBTree


# combine both in one or separate?
class Index:

    def __init__(self, table, col_idx, idx_type):
        self.index = None
        self.type = idx_type
        if idx_type == "Hash":
            self.index = {}
        else:
            self.index = OOBTree()

        for i, row in enumerate(table.rows):
            self.index[row[col_idx]] = (i, col_idx)

    def get_pos(self, key):
        return self.index[key]

    def print(self, f=None):
        for i in self.index.keys():
            print("%-10s -> %s" % (i, self.index[i]), file=f)


# class HashIndex:
#
#     def __init__(self, table, col_idx):
#         self.index = {}
#
#     def get_pos(self):
#         pass
#
#     def print(self, f=None):
#         print(self.index, file=f)
#
#
# class BtreeIndex:
#
#     def __init__(self, table, col_idx):
#         self.index = OOBTree()
#
#     def get_pos(self):
#         pass
#
#     def print(self, f=None):
#         print(self.index, file=f)
