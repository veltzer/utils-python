#!/usr/bin/env python
import pymysql.cursors

import myutils

REORDER_SQL = "SELECT * FROM TbWkWorkType ORDER BY name"
REORDER_CLAUSE = "ORDER BY name"
DB_TABLE_NAME = "TbWkWorkType"
ID_FIELD = "id"
FIELD_LIST = "name,remark,isVideo,isAudio,isLive,isText"
START = 1
DEBUG = True


def main() -> None:
    db_table_temp = f"{DB_TABLE_NAME}_temp"
    dbh = myutils.db_connect()
    try:
        with dbh.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(REORDER_SQL)
            rows = cursor.fetchall()
            counter = START
            hash_map = {}
            for row in rows:
                row_id = row[ID_FIELD]
                hash_map[row_id] = counter
                if DEBUG:
                    print(f"setting {row_id} to {counter}")
                counter += 1
            max_val = counter
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute(f"RENAME TABLE {DB_TABLE_NAME} TO {db_table_temp}")
            cursor.execute(f"CREATE TABLE {DB_TABLE_NAME} LIKE {db_table_temp}")
            insert_sql = f"INSERT INTO {DB_TABLE_NAME} ({FIELD_LIST}) SELECT {FIELD_LIST} FROM {db_table_temp} {REORDER_CLAUSE}"
            cursor.execute(insert_sql)
            cursor.execute(f"DROP TABLE {db_table_temp}")
            table_fkfix = "TbWkWork"
            field_fkfix = "typeId"
            cursor.execute(
                f"UPDATE {table_fkfix} SET {field_fkfix}={field_fkfix}+{max_val}"
            )
            for i in range(START, counter):
                newval = hash_map.get(i)
                if newval is not None:
                    cursor.execute(
                        f"UPDATE {table_fkfix} SET {field_fkfix}=%s WHERE {field_fkfix}=%s",
                        (newval, i + max_val),
                    )
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        dbh.commit()
    finally:
        dbh.close()


if __name__ == "__main__":
    main()
