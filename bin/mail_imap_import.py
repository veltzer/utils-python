#!/usr/bin/python3

'''
This script imports mail in maildir format to an imap server.

Restructuring the flow of this app:
- parse parameters from the command line.
- login to imap.
- recursively traverse the folder given.
- any file which is an email copy to gmail.

TODO:
- do real progress report - find number of files to be imported
    in advance and report on progress.
- do watchdog for connections hanging.
- make an rmdir executable to remove a directory on the imap server.
    (make it in this executable using subcommands of argparser).
'''

import configparser # for ConfigParser
import os.path # for expanduser
import argparse # for ArgumentParser, ArgumentDefaultsHelpFormatter
import imap.imap # for IMAP
import sys # for exit

########
# code #
########
cp = configparser.ConfigParser()
cp.read(os.path.expanduser('~/.details.ini'))
opt_username = cp.get('google', 'username')
opt_password = cp.get('google_imap', 'password')
opt_hostname = cp.get('google_imap', 'hostname')
opt_port = cp.get('google_imap', 'port')
opt_database = None

parser=argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument('--debug', help='do you want to debug the script?', default=False, action='store_true')
parser.add_argument('--exit', help='exif after debug?', default=False, action='store_true')
parser.add_argument('--noprogress', help='dont report progress', default=False, action='store_true')

subparsers=parser.add_subparsers(
    title='subcommands',
    dest='subcommand',
)

subparser_import=subparsers.add_parser(
    'import',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
subparser_import.add_argument('--mailfolder', help='folder where the mail is', default='~/Mail')
subparser_import.add_argument('--toplevel', help='tag under which to import', default='imap_import', action='store_true')
    
subparser_test=subparsers.add_parser(
    'test',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
    
subparser_rmdir=subparsers.add_parser(
    'rmdir',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
subparser_rmdir.add_argument('--toplevel', help='tag which to remove', default='imap_import', action='store_true')

args=parser.parse_args()

if args.debug:
    print('opt_username:', opt_username)
    print('opt_password:', opt_password)
    print('opt_hostname:', opt_hostname)
    print('opt_port:', opt_port)
    print(args)
if args.exit:
    sys.exit(0)

imp=imap.imap.IMAP()

imp.connect(opt_hostname, opt_port)
imp.login(opt_username, opt_password)

if args.subcommand=='import':
    imp.import_folder(os.path.expanduser(args.mailfolder), args.toplevel, not args.noprogress)
if args.subcommand=='test':
    imp.test()
if args.subcommand=='rmdir':
    imp.rmdir()

imp.logout()
