#!/usr/bin/env python
import argparse
import pprint

import pymysql
import pymysql.cursors

import myutils

DEBUG = True


def get_fields(dbh: pymysql.Connection, table: str) -> dict[str, None]:  # type: ignore[name-defined]
    if DEBUG:
        print(f"table is {table}")
    sql = "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND table_schema=DATABASE()"
    hash_map: dict[str, None] = {}
    with dbh.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(sql, (table,))
        for row in cursor.fetchall():
            column_name = row["column_name"]
            hash_map[column_name] = None
    if DEBUG:
        pprint.pprint(hash_map)
    return hash_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Get fields from a MySQL table.")
    parser.add_argument("--rcfile", help="Path to config file")
    parser.add_argument("--table", required=True, help="Table name")
    args = parser.parse_args()
    dbh = myutils.db_connect()
    try:
        get_fields(dbh, args.table)
    finally:
        dbh.close()


if __name__ == "__main__":
    main()
