#!/usr/bin/python


from subprocess import check_call
from subprocess import check_output
import re
import sys


class Git(object):
    def __init__(self):
        pass

    @classmethod
    def _exec(cls, arguments, exception=True, stdout=sys.stdout, stderr=sys.stderr):
        print(' '.join(arguments))
        try:
            check_call(arguments, stdout=stdout, stderr=stderr)
        except CalledProcessError as ex:
            print("Caught exception calling '{0}': {1}".format(' '.join(arguments), ex))
            if exception:
                raise ex

        return True

    @classmethod
    def _exec_output(cls, arguments, exception=True):
        print("Calling: '{0}'".format(' '.join(arguments)))
        try:
            output = check_output(arguments)
            print("Returned:\n{0}".format(output))
        except CalledProcessError as ex:
            print("Caught exception: '{0}'".format(ex))
            if exception:
                raise ex

        return output


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
        return Git._exec(['git', 'status'], exception=False)

    @staticmethod
    def lfs_fetch():
        return Git._exec(['git', 'lfs', 'fetch'])

    @staticmethod
    def apply(diff):
        return Git._exec(['git', 'apply', '--ignore-space-change', '--ignore-whitespace', diff])

    @staticmethod
    def validate_ref(ref_name):
        return Git._exec(['git', 'show', '--format=oneline', '--no-patch', 'origin/' + ref_name, '--'], exception=False) or \
               Git._exec(['git', 'show', '--format=oneline', '--no-patch', ref_name, '--'], exception=False)

    @staticmethod
    def get_remotes():
        output = Git._exec_output(['git', 'remote', '-v'])

        # Use regex to find remote URL (fetch)
        remotes = { "fetch": {}, "pull": {}}
        for line in output.split('\n'):
            matches = re.match("(\S+)\s+https://github.com/(.*)/(.*)\.git\s+\((fetch|pull)\)", line)
            if matches:
                g = matches.groups()
                alias, account, repository, direction = matches.groups()[:4]
                remotes[direction][alias] = (account, repository)

        return remotes

    @staticmethod
    def add_remote(alias, account, repository):

        url = "https://github.com/{0}/{1}.git".format(account, repository)
        Git._exec(['git', 'remote', 'add', alias, url])

        return