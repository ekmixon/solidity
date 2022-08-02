#! /usr/bin/env python3

"""
Performs pylint on all python files in the project repo's {test,script,docs} directory recursively.

This script is meant to be run from the CI but can also be easily in local dev environment,
where you can optionally pass `-d` as command line argument to let this script abort on first error.
"""


from os import path, walk, system
from sys import argv, exit as exitwith

PROJECT_ROOT = path.dirname(path.realpath(__file__))
PYLINT_RCFILE = f"{PROJECT_ROOT}/pylintrc"

SGR_INFO = "\033[1;32m"
SGR_CLEAR = "\033[0m"

def pylint_all_filenames(dev_mode, rootdirs):
    """ Performs pylint on all python files within given root directory (recursively).  """
    filenames = []
    for rootdir in rootdirs:
        for rootpath, _, filenames_w in walk(rootdir):
            filenames.extend(
                path.join(rootpath, filename)
                for filename in filenames_w
                if filename.endswith('.py')
            )

    failed = []
    for checked_count, filename in enumerate(filenames, start=1):
        cmdline = f'pylint --rcfile=\"{PYLINT_RCFILE}\" \"{filename}\"'
        print(
            f"{SGR_INFO}[{checked_count}/{len(filenames)}] Running pylint on file: {filename}{SGR_CLEAR}"
        )

        exit_code = system(cmdline)
        if exit_code != 0:
            if dev_mode:
                return 1, checked_count
            failed.append(filename)

    return len(failed), len(filenames)

def main():
    """ Collects all python script root dirs and runs pylint on them. You can optionally
        pass `-d` as command line argument to let this script abort on first error. """
    dev_mode = len(argv) == 2 and argv[1] == "-d"
    failed_count, total_count = pylint_all_filenames(
        dev_mode,
        [
            path.abspath(f"{path.dirname(__file__)}/../docs"),
            path.abspath(f"{path.dirname(__file__)}/../scripts"),
            path.abspath(f"{path.dirname(__file__)}/../test"),
        ],
    )

    if failed_count != 0:
        exitwith(f"pylint failed on {failed_count}/{total_count} files.")
    else:
        print(f"Successfully tested {total_count} files.")

if __name__ == "__main__":
    main()
