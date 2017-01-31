#!/usr/bin/python

from __future__ import print_function
import argparse
import os
import shutil
import stat
import sys
from subprocess import call

IFDM = 'InstituteforDiseaseModeling'


class Git:
    def __init__(self):
        Git._retval = 0
        pass

    @classmethod
    def _exec(cls, arguments, exception=True, stdout=sys.stdout, stderr=sys.stderr):
        print(' '.join(arguments))
        result = call(arguments, stdout=stdout, stderr=stderr)
        if exception and result != 0:
            raise UserWarning('{0} failed'.format(' '.join(arguments)))
        return result

    @staticmethod
    def lfs_clone(url, destination=None, out=sys.stdout, err=sys.stderr):
        destination = destination if destination is not None else os.getcwd()
        return Git._exec(['git', 'lfs', 'clone', url, destination], True, stdout=out, stderr=err)

    @staticmethod
    def checkout(branch='master'):
        return Git._exec(['git', 'checkout', branch])

    @staticmethod
    def reset(branch='master'):
        return Git._exec(['git', 'reset', '--hard', 'origin/' + branch])

    @staticmethod
    def fetch():
        return Git._exec(['git', 'fetch'])

    @staticmethod
    def status():
        return Git._exec(['git', 'status'], exception=False) == 0

    @staticmethod
    def lfs_fetch():
        return Git._exec(['git', 'lfs', 'fetch'])

    @staticmethod
    def apply(diff):
        return Git._exec(['git', 'apply', '--ignore-space-change', '--ignore-whitespace', diff])

    @staticmethod
    def validate_ref(ref_name):
        return Git._exec(['git', 'show', '--format=oneline', '--no-patch', 'origin/' + ref_name, '--'], exception=False) == 0 or \
               Git._exec(['git', 'show', '--format=oneline', '--no-patch', ref_name, '--'], exception=False) == 0


def main(arguments):

    dump_arguments(arguments)
    succeeded = True

    try:
        os.chdir(arguments.drive)

        # if working directory exists but account isn't IfDM, delete the working directory
        if os.path.exists(arguments.directory):
            shutil.rmtree(arguments.directory, onerror=remove_readonly)

        # Working directory should not exist now, create it
        os.makedirs(arguments.directory)

        os.chdir(arguments.directory)

        # if working directory isn't a Git repository, clone the specified repository
        # https://user:password@github.com/account/repository.git
        url = 'https://{0}{1}@github.com/{2}/{3}.git'.format(
            arguments.user,
            ':' + arguments.password if arguments.password is not None else '',
            arguments.account,
            arguments.repository)

        # We'll use lfs_clone() since it works on both 'regular' repositories and ones using LFS.
        # Git.lfs_clone(url, out=open(os.devnull, 'w'), err=open(os.devnull, 'w'))
        Git.lfs_clone(url)
        Git.fetch()     # Make sure our view matches the GitHub view

        # checkout the specific commit (via branch, hash, or tag)
        if Git.validate_ref(arguments.commit):
            Git.checkout(arguments.commit)
            Git.lfs_fetch()  # LFS fetch to populate the files with their content rather than metadata, if appropriate
        else:
            raise UserWarning("Specified commit, '{0}', doesn't appear to be a branch, tag, or commit hash.".format(arguments.commit))

    except UserWarning as warn:
        print(warn, file=sys.stderr)
        succeeded = False

    return 0 if succeeded else -1


def dump_arguments(arguments):
    print("Working drive:            '{0}'".format(arguments.drive))
    print("Working directory:        '{0}'".format(arguments.directory))
    print("GitHub user:              '{0}'".format(arguments.user))
    print("GitHub password is {0}set.".format('not ' if arguments.password is None else ''))
    print("GitHub account:           '{0}'".format(arguments.account))
    print("GitHub repository:        '{0}'".format(arguments.repository))
    print("Target branch/commit/tag: '{0}'".format(arguments.commit))

    return


def remove_readonly(func, path, excinfo):
    """
    Helper for shutil.rmtree() since some files from GitHub are marked readonly.
    :param func:    function which raised the exception
    :param path:    path name passed to function
    :param excinfo: exception information
    :return: None
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

    return

'''
Get a copy of the code to build from a specific account, repository, and branch (all hosted on GitHub):
1) Specify GitHub account
2) Specify repository name
3) Specify branch|commit|tag
4) Working directory may or may not exist, if it exists it may or may not represent the current state of the specified
   account/repository and branch.
5) Will not (no longer) support applying patch files.
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', required=True, help='Working directory, not including drive letter')
    parser.add_argument('-v', '--drive', default=os.path.splitdrive(os.getcwd())[0],
                        help="Working drive letter, e.g. 'D:'")
    parser.add_argument('-u', '--user', required=True, help='GitHub user name')
    parser.add_argument('-p', '--password', default=None, help='GitHub user password')
    parser.add_argument('-a', '--account', default='InstituteforDiseaseModeling', help='GitHub account name')
    parser.add_argument('-r', '--repository', default='DtkTrunk', help='Repository name')
    parser.add_argument('-c', '--commit', default='master', help='Commit ID - branch name, commit hash, or tag')

    args = parser.parse_args()

    sys.exit(main(args))
