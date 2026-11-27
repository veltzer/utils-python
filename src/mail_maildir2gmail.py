#!/usr/bin/env python

"""Upload email messages from a list of Maildir to Google Mail."""

import argparse
import contextlib
import dbm
import email
import email.header
import email.utils
import getpass
import os
import sys
import time
from argparse import Namespace
from dbm import _Database
from imaplib import IMAP4_SSL
from time import struct_time


class Gmail:
    def __init__(self, options: Namespace) -> None:
        self.username = options.username
        self.password = options.password
        self.folder = options.folder
        if self.folder == "inbox":
            self.folder = "INBOX"
        else:
            pass

        self.__imap: IMAP4_SSL | None = None

    def __del__(self) -> None:
        if self.__imap is not None:
            with contextlib.suppress(Exception):
                self.__imap.close()
                self.__imap.logout()
            self.__imap = None

    def append(self, filename: str) -> None:
        if self.check_appended(filename):
            return

        with open(filename, "rb") as f:
            content = f.read()

        if content.endswith(b"\x00\x00\x00"):
            log(f"Skipping [{os.path.basename(filename)}] - corrupted")
            return

        message = email.message_from_bytes(content)
        timestamp = parsedate(message["date"])
        if not timestamp:
            log(f"Skipping [{os.path.basename(filename)}] - no date")
            return

        subject = decode_header(message["subject"])
        log(f"Sending [{subject}] ([{len(content)}] bytes)")
        del message

        print(self.folder)
        print(self.imap.append(self.folder, "(\\Seen)", timestamp, content))
        self.mark_appended(filename)

    def check_appended(self, filename: str) -> bool:
        with self.open_database() as database:
            return os.path.basename(filename).encode("utf-8") in database

    def mark_appended(self, filename: str) -> None:
        with self.open_database() as database:
            database[os.path.basename(filename).encode("utf-8")] = b"1"

    def open_database(self) -> _Database:
        dbname = os.path.abspath(os.path.splitext(sys.argv[0])[0] + ".db")
        return dbm.open(dbname, "c")

    @property
    def imap(self) -> IMAP4_SSL:
        if self.__imap is None:
            if not self.username or not self.password:
                raise LookupError("Username/password not supplied")

            self.__imap = IMAP4_SSL("imap.gmail.com")
            self.__imap.login(self.username, self.password)
            log("Connected to Gmail IMAP")
        return self.__imap


def decode_header(value: str) -> str:
    result = []
    for part, charset in email.header.decode_header(value):
        if isinstance(part, str):
            result.append(part)
            continue
        try:
            text = part.decode() if charset is None else part.decode(charset)
        except UnicodeError, LookupError:
            text = part.decode("iso-8859-1")
        result.append(text)
    return " ".join(result)


def encode_unicode(value: str | bytes) -> str | bytes:
    if isinstance(value, str):
        for codec in ["iso-8859-1", "utf8"]:
            try:
                return value.encode(codec)
            except UnicodeError:
                pass

    return value


def log(message: str) -> None:
    t = time.strftime("%H:%M:%S")
    print(f"[{t}]: {encode_unicode(message)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--folder", help="Folder to store the emails", default="All Mail"
    )
    parser.add_argument(
        "--username", help="Username to log into Gamil", default="username"
    )
    args, dirnames = parser.parse_known_args()
    args.password = getpass.getpass("Password: ")

    gmail = Gmail(args)
    for dirname in dirnames:
        for entry in os.listdir(dirname):
            filename = os.path.join(dirname, entry)
            if os.path.isfile(filename):
                try:
                    gmail.append(filename)
                except Exception:
                    log(f"Unable to send [{filename}]")
                    raise


def parsedate(value: str) -> struct_time | None:
    if not value:
        return None
    parsed = email.utils.parsedate_tz(decode_header(value))
    if parsed is not None:
        timestamp = email.utils.mktime_tz(parsed)
        return time.localtime(timestamp)
    return None


if __name__ == "__main__":
    main()
