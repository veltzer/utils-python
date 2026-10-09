#!/usr/bin/env python
import pymysql.cursors

import myutils


def to_slug(val: str) -> str:
    return "-".join(val.lower().split())


def main() -> None:
    param_table = "TbBsCompanies"
    param_field_from = "name"
    param_field_to = "slug"
    dbh = myutils.db_connect()
    try:
        with dbh.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = f"SELECT {param_field_from} FROM {param_table}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                field_val = row[param_field_from]
                if field_val:
                    new_slug = to_slug(field_val)
                    update_sql = f"UPDATE {param_table} SET {param_field_to}=%s WHERE {param_field_from}=%s"
                    cursor.execute(update_sql, (new_slug, field_val))
        dbh.commit()
    finally:
        dbh.close()


if __name__ == "__main__":
    main()
