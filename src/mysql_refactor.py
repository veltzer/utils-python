#!/usr/bin/env python
import pymysql.cursors

import myutils


def main() -> None:
    dbh = myutils.db_connect()
    orig_hash: dict[str, int] = {}
    try:
        with dbh.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM TbWkWork")
            rows = cursor.fetchall()
            for row in rows:
                row_id = row["id"]
                fname = row.get("author_firstname", "")
                sname = row.get("author_surname", "")
                name = f"{fname} {sname}"
                if name in orig_hash:
                    new_id = orig_hash[name]
                else:
                    insert_sql = "INSERT INTO TbIdPerson (firstname, surname, othername) VALUES (%s, %s, %s)"
                    cursor.execute(
                        insert_sql, (fname, sname, row.get("author_othername", ""))
                    )
                    new_id = cursor.lastrowid
                    orig_hash[name] = new_id
                update_sql = "UPDATE TbWkWork SET authorId=%s WHERE id=%s"
                cursor.execute(update_sql, (new_id, row_id))
        dbh.commit()
    finally:
        dbh.close()


if __name__ == "__main__":
    main()
