#!/usr/bin/python

from __future__ import print_function
import argparse
from subprocess import check_call
from subprocess import check_output
import tempfile
from gitClass import Git


def main(arguments):

    try:
        # Execute "git remote -v"
        command = "git remote -v"
        output = check_output(command)
        print("'{0}' returned:\n{1}".format(command, output))

        remotes = Git.get_remotes()['fetch']

        # Look for account in URL
        alias = None
        for remote in remotes:
            account, repository = remotes[remote]
            # If found, map remote name for account and repository
            if (account == arguments.account) and (repository == arguments.repository):
                alias = remote
                print("Found remote for account {0} and repository {1}: {2}".format(account, repository, remote))

        # If not found, add remote and map remote name for account and repository
        if alias is None:
            print("Didn't find remote for account {0} and repository {1}, adding...".format(arguments.account, arguments.repository))
            Git.add_remote(arguments.account, arguments.account, arguments.repository)  # use account for alias

    except Exception as e:
        print("git remote failed: '{0}'".format(e))

    return
  

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--account", default="InstituteforDiseaseModeling", help="GitHub account name (e.g. 'InstituteforDiseaseModeling' or 'clorton')")
    parser.add_argument("-r", "--repository", default="DtkTrunk", help="Git repository (e.g. 'DtkTrunk' or 'EMOD-Typhoid'")
    args = parser.parse_args()
    main(args)
