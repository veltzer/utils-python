#!/usr/bin/python3

"""Upload email messages from a list of Maildir to Google Mail."""

import email
import email.header
import email.utils
import os
import sys
import time
from imaplib import IMAP4_SSL
import argparse
import bsddb3


class Gmail:
    def __init__(self, options):
        self.username = options.username
        self.password = options.password
        self.folder = options.folder
        if self.folder == "inbox":
            self.folder = "INBOX"
        else:
            # self.folder = '[Gmail]/%s' % self.folder
            pass

        self.__database = None
        self.__imap = None

    def __del__(self):
        if self.__database is not None:
            # pylint: disable=broad-except
            try:
                self.__database.close()
            except Exception:
                pass
            self.__database = None

        if self.__imap is not None:
            # pylint: disable=broad-except
            try:
                self.__imap.logout()
                self.__imap.close()
            except Exception:
                pass
            self.__imap = None

    def append(self, filename):
        if self.check_appended(filename):
            return

        with open(filename, "rb") as f:
            content = f.read()

        if content.endswith("\x00\x00\x00"):
            log(f"Skipping [{os.path.basename(filename)}] - corrupted")
            return

        message = email.message_from_string(content)
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
        return os.path.basename(filename) in self.database

    def mark_appended(self, filename):
        self.database[os.path.basename(filename)] = "1"

    @property
    def database(self):
        if self.__database is None:
            dbname = os.path.abspath(os.path.splitext(sys.argv[0])[0] + ".db")
            self.__database = bsddb3.btopen(dbname, "w")
        return self.__database

    @property
    def imap(self):
        if self.__imap is None:
            if not self.username or not self.password:
                raise Exception("Username/password not supplied")

            self.__imap = IMAP4_SSL("imap.gmail.com")
            self.__imap.login(self.username, self.password)
            log("Connected to Gmail IMAP")
        return self.__imap


def decode_header(value):
    result = []
    for v, c in email.header.decode_header(value):
        try:
            if c is None:
                v = v.decode()
            else:
                v = v.decode(c)
        except (UnicodeError, LookupError):
            v = v.decode("iso-8859-1")
        result.append(v)
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
    print(f"[{time.strftime('%H:%M:%S')}]: {encode_unicode(message)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--folder", help="Folder to store the emails", default="All Mail"
    )
    parser.add_argument(
        "--password", help="Password to log into Gmail", default="password"
    )
    parser.add_argument(
        "--username", help="Username to log into Gamil", default="username"
    )
    args = parser.parse_args()

    args, dirnames = parser.parse_known_args()

    gmail = Gmail(args)
    for dirname in dirnames:
        for filename in os.listdir(dirname):
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                try:
                    gmail.append(filename)
                except Exception as e:
                    log(f"Unable to send [{filename}]")
                    raise e


def parsedate(value):
    value = decode_header(value)
    value = email.utils.parsedate_tz(value)
    if isinstance(value, tuple):
        timestamp = time.mktime(tuple(value[:9]))
        if value[9]:
            timestamp -= time.timezone + value[9]
            if time.daylight:
                timestamp += 3600
        return time.localtime(timestamp)
    raise ValueError(f"value {value} is bad")


if __name__ == "__main__":
    main()
