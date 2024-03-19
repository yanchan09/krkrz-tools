import sys
import argparse
from cx3.hashdb import HashDatabase
from cx3.table import ArchiveTable

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(prog="tabledump")
    parser.add_argument("filename")
    parser.add_argument("-d", "--hashdb")
    args = parser.parse_args()

    hdb = None
    if args.hashdb:
        hdb = HashDatabase(args.hashdb)

    with open(args.filename, "rb") as f:
        data = f.read()

    table = ArchiveTable(data)
    table.dump(hdb)
