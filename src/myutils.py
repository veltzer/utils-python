import configparser
from pathlib import Path

import dateutil.parser
import pymysql


def to_mysql(string: str) -> str:
    dt = dateutil.parser.parse(string)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def show_menu(options: list[str]) -> str:
    while True:
        for entry in options:
            print(entry)
        try:
            response = input().strip()
        except EOFError as err:
            raise RuntimeError("eof reached") from err
        if len(response) != 1:
            continue
        for entry in options:
            if response == entry[0]:
                return response
        print("bad response")


def show_yes_no_dialog(question: str) -> bool:
    while True:
        print(question, end="", flush=True)
        try:
            response = input().strip()
        except EOFError:
            return False
        if response in ("y", "n"):
            return response == "y"


def get_from_user(message: str) -> str:
    print(message, end="", flush=True)
    try:
        return input().strip()
    except EOFError:
        return ""


def delete_work(dbh: pymysql.Connection, f_id: int) -> None:  # type: ignore[name-defined]
    queries = [
        "DELETE FROM TbWkWorkAuthorization WHERE workId=%s",
        "DELETE FROM TbWkWorkChapter WHERE workId=%s",
        "DELETE FROM TbWkWorkContrib WHERE workId=%s",
        "DELETE FROM TbWkWorkExternal WHERE workId=%s",
        "DELETE FROM TbWkWorkViewPerson WHERE viewId IN (SELECT id FROM TbWkWorkView WHERE workId=%s)",
        "DELETE FROM TbWkWorkView WHERE workId=%s",
        "DELETE FROM TbWkWorkReview WHERE workId=%s",
        "DELETE FROM TbWkWorkAlias WHERE workId=%s",
        "DELETE FROM TbWkWork WHERE id=%s",
    ]
    with dbh.cursor() as cursor:
        for query in queries:
            cursor.execute(query, (f_id,))


def db_connect() -> pymysql.Connection:  # type: ignore[name-defined]
    rcfile = Path.home() / ".perlmyworld.ini"
    cfg = configparser.ConfigParser()
    if not cfg.read(rcfile):
        raise RuntimeError(f"unable to access ini file {rcfile}")
    param_user = cfg.get("myworld", "username", fallback=None)
    param_pass = cfg.get("myworld", "password", fallback=None)
    param_host = cfg.get("myworld", "hostname", fallback="localhost")
    param_port = cfg.getint("myworld", "port", fallback=3306)
    param_name = cfg.get("myworld", "name", fallback=None)
    if not param_user or not param_pass or not param_name:
        raise RuntimeError("Missing required db configuration")
    return pymysql.connect(
        host=param_host,
        port=param_port,
        user=param_user,
        password=param_pass,
        database=param_name,
        autocommit=False,
        charset="utf8mb4",
    )
