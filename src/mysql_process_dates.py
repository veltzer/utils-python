#!/usr/bin/env python
import pymysql.cursors

import myutils

P_TABLE = "TbWkWork"
P_READ_COLUMN = "viewdate"
P_ID_COLUMN = "id"
P_WRITE_COLUMN = "viewdatesub"
DEBUG = True


def unixdate_to_mysql(string: str) -> str:
    return myutils.to_mysql(string)


def main() -> None:
    dbh = myutils.db_connect()
    try:
        with dbh.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f"SELECT {P_ID_COLUMN}, {P_READ_COLUMN} FROM {P_TABLE}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                row_id = row[P_ID_COLUMN]
                viewdate = row[P_READ_COLUMN]
                if DEBUG:
                    print(f"got date {viewdate}")
                if viewdate:
                    newdate = unixdate_to_mysql(viewdate)
                    if DEBUG:
                        print(f"newdate is {newdate}")
                    update_sql = f"UPDATE {P_TABLE} SET {P_WRITE_COLUMN}=%s WHERE {P_ID_COLUMN}=%s"
                    cursor.execute(update_sql, (newdate, row_id))
        dbh.commit()
    finally:
        dbh.close()


if __name__ == "__main__":
    main()
