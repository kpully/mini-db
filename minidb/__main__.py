import sys
import time
from minidb.argparser import ArgParser
from minidb.database import Database as mdb
from minidb.utils import Utils as utils
data_path = "data/"


def start():
    db = mdb()

    with open("output.txt", "w"):
        print()

    while True:
        try: 
            txt = input("\nminidb>> ")

            start_time = time.time()

            # handle special commands which don't require further parsing
            if txt == "exit":
                break

            elif txt == "show_tables":
                db.show_tables()
                continue

            elif txt == "show_index":
                db.show_index()
                continue
        
            # handle other commands after parsing
            table_name, cmd, args = utils.parse(txt)

            # there were only comments in the input text
            if cmd is None:
                continue

            in_table, columns, criteria = ArgParser(cmd, args).get_args()

            if cmd == "count":
                db.count(table_name, in_table)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "inputfromfile":
                db.input_from_file(table_name, data_path + in_table)

            elif cmd == "outputtofile":
                db.output_to_file(in_table[0], columns[0])

            elif cmd == "select":
                db.select(table_name, in_table, criteria)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "project":
                db.project(table_name, in_table[0], columns)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "concat":
                db.concat(table_name, in_table)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "sort":
                db.sort(table_name, in_table[0], columns)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "join":
                db.join(table_name, in_table, criteria)
                db.output_to_file(table_name, "output.txt")
                end_time = time.time()
                db.tables[table_name].print()
                print("\nTime taken: %0.5f s" % (end_time - start_time))
                with open("output.txt", "a") as f:
                    print("\nTime taken: %0.5f s" % (end_time - start_time), file=f)
                continue

            elif cmd == "avggroup":
                db.avggroup(table_name, in_table[0], columns[0], columns[1:])
                db.output_to_file(table_name, "output.txt")

            elif cmd == "sumgroup":
                db.sumgroup(table_name, in_table[0], columns[0], columns[1:])
                db.output_to_file(table_name, "output.txt")

            elif cmd == "countgroup":
                db.countgroup(table_name, in_table[0], columns[0], columns[1:])
                db.output_to_file(table_name, "output.txt")

            elif cmd == "movavg":
                n = int(criteria)
                db.movavg(table_name, in_table[0], columns, n)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "movsum":
                n = int(criteria)
                db.movsum(table_name, in_table[0], columns, n)
                db.output_to_file(table_name, "output.txt")

            elif cmd == "avg":
                db.avg(table_name, in_table[0], columns[0])
                db.output_to_file(table_name, "output.txt")

            elif cmd == "sum":
                db.sum(table_name, in_table[0], columns[0])
                db.output_to_file(table_name, "output.txt")

            elif cmd == "Btree":
                db.Btree(in_table[0], columns[0])

            elif cmd == "Hash":
                db.Hash(in_table[0], columns[0])

            else:  # default
                print("Wrong command. Use help to find out the correct usage")

            end_time = time.time()

            print("\nTime taken: %0.5f s" % (end_time - start_time))
            with open("output.txt", "a") as f:
                print("\nTime taken: %0.5f s\n\n" % (end_time - start_time), file=f)


        except ValueError as e:
            continue

        except EOFError as e:
            print(e)
            break
        

if __name__ == "__main__":
    start()
