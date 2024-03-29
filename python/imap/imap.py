"""
module to help with imap.

Tecnically this is a wrapper object.

To see the documentation of the API use: pydoc imaplib
This thing started from me wanting to import my old mail to gmail and seeing
this blog post: http://scott.yang.id.au/2009/01/migrate-emails-maildir-gmail.html

Refrences:
http://stackoverflow.com/questions/3180891/imap-deleting-messages
"""

import imaplib
import dbm.gnu

import os.path
import os
import email
import email.utils
import email.header
import time

# db functions


def db_open():
    dbname = os.path.expanduser('~/.imap_import.db')
    # pylint: disable=no-member
    return dbm.gnu.open(dbname, 'c')


def db_have(filename, opt_database):
    return filename in opt_database


def db_mark(filename, opt_database):
    opt_database[filename] = '1'


def db_close(opt_database):
    opt_database.close()

# general helpers


def decode_header(value):
    result = []
    for v, c in email.header.decode_header(value):
        try:
            if c is None:
                v = v.decode()
            else:
                v = v.decode(c)
        except (UnicodeError, LookupError):
            v = v.decode('iso-8859-1')
        result.append(v)
    return " ".join(result)


def parsedate(value):
    value = decode_header(value)
    value = email.utils.parsedate_tz(value)
    timestamp = time.mktime(tuple(value[:9]))
    if value[9]:
        timestamp -= time.timezone + value[9]
        if time.daylight:
            timestamp += 3600
    return time.localtime(timestamp)

# imap functions


class IMAP:

    def __init__(self):
        self.db = None
        self.imap = None

    def connect(self, opt_hostname, opt_port):
        self.imap = imaplib.IMAP4_SSL(opt_hostname, opt_port)

    def login(self, username, password):
        (res, _) = self.imap.login(username, password)
        if res != 'OK':
            raise ValueError(f"could not login with error [{res}]")
        self.db = db_open()

    def logout(self):
        db_close(self.db)
        (res, _) = self.imap.logout()
        if res != 'BYE':
            raise ValueError(f"could not logout with error [{res}]")

    def have(self, name):
        """
        check if we have a single folder. if you pass 'a/b' it will check if you have a SINGLE
        folder called 'a/b'...
        """
        (res, l) = self.imap.list(name)
        if res != 'OK':
            raise ValueError(f"could not list [{name}]. error is [{l[0].decode()}]")
        if len(l) == 1 and l[0] is None:
            return False
        return True

    def create(self, name):
        """
        this function creates a single folder.
        if the folder exists then it will throw an exception
        """
        (res, l) = self.imap.create(name)
        if res != 'OK':
            raise ValueError(f"could not list [{name}]. error is [{l[0].decode()}]")

    def delete(self, name):
        """
        this function deletes a single folder.
        If the folder doesn't exist then it will throw an exception
        """
        (res, l) = self.imap.delete(name)
        if res != 'OK':
            raise ValueError(f"could not list [{name}]. error is [{l[0].decode()}]")

    def have_fullpath(self, path):
        '''
        check that we have a full path. Returns boolean to indicate the state.
        '''
        parts = path.split('/')
        for x in range(1, len(parts) + 1):
            cur = '/'.join(parts[:x])
            if not self.have(cur):
                return False
        return True

    def create_fullpath_db(self, path):
        '''
        create a full path and remember which paths have been created in a set
        '''
        parts = path.split('/')
        for x in range(1, len(parts) + 1):
            cur = '/'.join(parts[:x])
            if not db_have(cur, self.db):
                if not self.have(cur):
                    self.create(cur)
                db_mark(cur, self.db)

    def create_fullpath(self, path):
        '''
        create a full path of folders. strict.
        '''
        parts = path.split('/')
        for x in range(1, len(parts) + 1):
            self.create('/'.join(parts[:x]))

    def delete_fullpath(self, path):
        '''
        delete a full path of folders. strict.
        '''
        parts = path.split('/')
        # note that delete is in reverse order
        for x in range(len(parts), 0, -1):
            cur = '/'.join(parts[:x])
            self.delete(cur)

    def append(self, mailbox, flags, date_time, message):
        '''
        append a single message to a mailbox
        '''
        (res, l) = self.imap.append(mailbox, flags, date_time, message)
        if res != 'OK':
            raise ValueError(f"could not append to [{mailbox}]. error is [{l[0].decode()}]")

    def append_file(self, mailbox, flags, filename):
        with open(filename, "rb") as f:
            content = f.read()
        message = email.message_from_string(content)
        timestamp = parsedate(message['date'])
        # subject = decode_header(message['subject'])
        self.append(mailbox, flags, timestamp, content)

    def test(self):
        """ test function """
        # this works
        print(self.imap.capability())
        print(self.imap.list())
        # this works
        assert not self.have('dontexist')
        assert self.have('business')
        # this works
        # now we try to delete a folder which does not exist.
        # this should raise an error. If it doesn't then we need to
        # error
        have_error = False
        try:
            self.delete('dontexist')
        except ValueError:
            have_error = True
        assert have_error

        # this works
        self.create('foo')
        assert self.have('foo')
        self.delete('foo')
        assert not self.have('foo')

        # this works
        # this creates a label called 'foo/bar' and not two labels one within the other
        self.create('foo/bar')
        self.delete('foo/bar')

        # this works
        self.create_fullpath('foo/bar/zoo')
        assert self.have('foo')
        assert self.have('foo/bar')
        assert self.have('foo/bar/zoo')
        self.delete_fullpath('foo/bar/zoo')
        assert not self.have('foo')
        assert not self.have('foo/bar')
        assert not self.have('foo/bar/zoo')

        # this should fail
        self.create('business')

        # this works
        assert self.have_fullpath('business/hinbit/projects/smartbuild')

        # this works
        # filename='/home/mark/Mail/.hobbies.directory/blog/cur/1279466171.2097.5oTh7:2,S'
        filename = 'support/test_mail_msg'
        self.create_fullpath('test/foo/bar/zoo')
        with open(filename, "rb") as f:
            content = f.read()
        self.append('test/foo/bar/zoo', None, None, content)

        # lets try this
        self.delete_fullpath('test/foo/bar/zoo')

    def import_folder(self, folder, toplevel, doprogress):
        for root, _, files in os.walk(folder):
            for file in files:
                if not file.endswith(',S'):
                    continue
                filename = os.path.join(root, file)
                assert os.path.isfile(filename)
                relpath = os.path.relpath(os.path.dirname(filename), folder)
                # calculate folder in gmail
                parts = relpath.split(os.path.sep)
                assert parts[-1] == 'cur'
                parts.pop()
                # all but the last folder element are of the form [.folder.directory]
                for i, part in enumerate(parts[:-1]):
                    assert part.endswith('.directory')
                    assert part.startswith('.')
                    parts[i] = part[1:-10]
                target_folder = '/'.join([toplevel, '/'.join(parts)])
                if doprogress:
                    print(f"filename is [{filename}]")
                    print(f"target_folder is [{target_folder}]")
                self.create_fullpath_db(target_folder)
                if not db_have(filename, self.db):
                    with open(filename, "rb") as f:
                        self.append(target_folder, None, None, f.read())
                    db_mark(filename, self.db)
