#!/usr/bin/python3

'''
This script runs 'make' (make(1)) in every project
that is mine.
'''

import os # for chdir, system
import os.path # for expanduser, isdir, isfile, join
import utils.github # for get_nonforked_repos
import subprocess # for check_call
import yaml # for loads
import sys # for exit

home=os.getenv('HOME')
print_all=True
stop_on_fail=False

projects=list()
filename=os.path.expanduser('~/.mrconfig')
for line in open(filename):
    line=line.rstrip()
    if line.startswith('['):
        project_root=os.path.join(home, line[1:-1])
        project_name=line[1:-1].split('/')[-1]
        projects.append((project_name, project_root))

project_options_file=os.path.expanduser('~/.mroptions.yaml')
if os.path.isfile(project_options_file):
    with open(project_options_file) as f:
        opts=yaml.load(f)
else:
    opts=dict()
#print(opts)
#sys.exit(1)

def run_check_string(args, string, string_to_print=None, exit=False, do_print=False):
    ''' this method runs make and checks that the output does not have lines with warnings in them '''
    p=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_out, res_err = p.communicate()
    res_out=res_out.decode()
    res_err=res_err.decode()
    error=False
    error_code=p.returncode
    if p.returncode:
        error=True
    if any(line.find(string)>0 for line in res_err.split()):
        error=True
        error_code=1
    if error:
        if string_to_print:
            print(string_to_print)
        if do_print:
            print(res_out, file=sys.stderr, end='')
            print(res_err, file=sys.stderr, end='')
        if exit:
            sys.exit(p.returncode)
    return error_code

def run_empty_output(args, string_to_print=None, exit=False, do_print=False):
    p=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_out, res_err = p.communicate()
    res_out=res_out.decode()
    res_err=res_err.decode()
    if p.returncode or res_out!='' or res_err!='':
        if string_to_print:
            print(string_to_print)
        if do_print:
            print(res_out, file=sys.stderr, end='')
            print(res_err, file=sys.stderr, end='')
        if exit:
            sys.exit(p.returncode)
    return p.returncode

#projects=[(repo.name, os.path.join(home,'git',repo.name)) for repo in utils.github.get_nonforked_repos_list()]

event_error = 0
event_ok = 0
event_makefile = 0
for project_name, project_root in projects:
    if not os.path.isdir(project_root):
        continue
    string_to_print='building [{0}] at [{1}]...'.format(project_name, project_root)
    if print_all:
        print(string_to_print, end='')
        sys.stdout.flush()
    makefile=os.path.join(project_root, 'Makefile')
    bootstrap=os.path.join(project_root, 'bootstrap')
    if os.path.isfile(makefile):
        os.chdir(project_root)
        check_empty_output=True
        if project_name in opts:
            if 'dont_check_empty_output' in opts[project_name]:
                check_empty_output=False
        if check_empty_output:
            code=run_empty_output(['make'])
            if code:
                print('ERROR')
                event_error += 1
                if stop_on_fail:
                    sys.exit(code)
            else:
                print('OK')
                event_ok += 1
        else:
            code=run_check_string(['make'], string='warning')
            if code:
                print('ERROR')
                event_error += 1
                if stop_on_fail:
                    sys.exit(code)
            else:
                print('OK')
                event_ok += 1
        #os.system('make')
    elif os.path.isfile(bootstrap):
        os.chdir(project_root)
        code = run_empty_output(['./bootstrap'])
        if code:
                print('ERROR')
                event_error += 1
                if stop_on_fail:
                    sys.exit(code)
                continue
        code = run_empty_output(['./configure'])
        if code:
                print('ERROR')
                event_error += 1
                if stop_on_fail:
                    sys.exit(code)
                continue
        code = run_empty_output(['make'])
        if code:
                print('ERROR')
                event_error += 1
                if stop_on_fail:
                    sys.exit(code)
                continue
        event_ok += 1
        print('OK')
    else:
        #print('dont know how to build [{0}]...'.format(project_name))
        print('MAKEFILE NOT FOUND')
        event_makefile += 1
        pass

print("event_makefile happened [{}]".format(event_makefile))
print("event_error happened [{}]".format(event_error))
print("event_ok happened [{}]".format(event_ok))
