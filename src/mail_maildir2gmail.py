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
from imaplib import IMAP4_SSL


class Gmail:
    def __init__(self, options):
        self.username = options.username
        self.password = options.password
        self.folder = options.folder
        if self.folder == "inbox":
            self.folder = "INBOX"
        else:
            # self.folder = "[Gmail]/%s" % self.folder
            pass

        self.__imap = None

    def __del__(self):
        if self.__imap is not None:
            with contextlib.suppress(Exception):
                self.__imap.close()
                self.__imap.logout()
            self.__imap = None

    def append(self, filename):
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

    def check_appended(self, filename):
        with self.open_database() as database:
            return os.path.basename(filename).encode("utf-8") in database

    def mark_appended(self, filename):
        with self.open_database() as database:
            database[os.path.basename(filename).encode("utf-8")] = b"1"

    def open_database(self):
        dbname = os.path.abspath(os.path.splitext(sys.argv[0])[0] + ".db")
        return dbm.open(dbname, "c")

    @property
    def imap(self):
        if self.__imap is None:
            if not self.username or not self.password:
                raise LookupError("Username/password not supplied")

            self.__imap = IMAP4_SSL("imap.gmail.com")
            self.__imap.login(self.username, self.password)
            log("Connected to Gmail IMAP")
        return self.__imap


def decode_header(value):
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


def encode_unicode(value):
    if isinstance(value, str):
        for codec in ["iso-8859-1", "utf8"]:
            try:
                value = value.encode(codec)
                break
            except UnicodeError:
                pass

    return value


def log(message):
    t = time.strftime("%H:%M:%S")
    print(f"[{t}]: {encode_unicode(message)}")


def main():
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


def parsedate(value):
    if not value:
        return None
    value = decode_header(value)
    value = email.utils.parsedate_tz(value)
    if value is not None:
        timestamp = email.utils.mktime_tz(value)
        return time.localtime(timestamp)
    return None


if __name__ == "__main__":
    main()
