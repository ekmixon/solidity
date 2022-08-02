#!/usr/bin/env python3
#
# This script reads C++ or RST source files and writes all
# multi-line strings into individual files.
# This can be used to extract the Solidity test cases
# into files for e.g. fuzz testing as
# scripts/isolate_tests.py test/libsolidity/*

import sys
import re
import os
import hashlib
from os.path import join, isfile, split

def extract_test_cases(path):
    lines = open(path, encoding="utf8", errors='ignore', mode='r', newline='').read().splitlines()

    inside = False
    delimiter = ''
    tests = []

    for l in lines:
        if inside:
            if l.strip().endswith(f'){delimiter}' + '";'):
                inside = False
            else:
                tests[-1] += l + '\n'
        elif m := re.search(r'R"([^(]*)\($', l.strip()):
            inside = True
            delimiter = m[1]
            tests += ['']

    return tests

# Contract sources are indented by 4 spaces.
# Look for `pragma solidity`, `contract`, `library` or `interface`
# and abort a line not indented properly.
def extract_docs_cases(path):
    insideBlock = False
    insideBlockParameters = False
    pastBlockParameters = False
    extractedLines = []
    tests = []

    # Collect all snippets of indented blocks
    for l in open(path, mode='r', errors='ignore', encoding='utf8', newline='').read().splitlines():
        if l != '':
            if not insideBlock and l.startswith(' '):
                # start new test
                extractedLines += ['']
                insideBlockParameters = False
                pastBlockParameters = False
            insideBlock = l.startswith(' ')
        if insideBlock:
            if not pastBlockParameters:
                if (
                    l.strip().startswith(':')
                    or l == ''
                    and insideBlockParameters
                ):
                    insideBlockParameters = True

                else:
                    insideBlockParameters = False
                    pastBlockParameters = True
            if not insideBlockParameters:
                extractedLines[-1] += l + '\n'

    codeStart = "(// SPDX-License-Identifier:|pragma solidity|contract.*{|library.*{|interface.*{)"

    # Filter all tests that do not contain Solidity or are indented incorrectly.
    for lines in extractedLines:
        if re.search(r'^\s{0,3}' + codeStart, lines, re.MULTILINE):
            print(f"Indentation error in {path}:")
            print(lines)
            exit(1)
        if re.search(r'^\s{4}' + codeStart, lines, re.MULTILINE):
            tests.append(lines)

    return tests

def write_cases(f, tests):
    cleaned_filename = f.replace(".","_").replace("-","_").replace(" ","_").lower()
    for test in tests:
        # When code examples are extracted they are indented by 8 spaces, which violates the style guide,
        # so before checking remove 4 spaces from each line.
        remainder = re.sub(r'^ {4}', '', test, 0, re.MULTILINE)
        sol_filename = f'test_{hashlib.sha256(test.encode("utf-8")).hexdigest()}_{cleaned_filename}.sol'

        open(sol_filename, mode='w', encoding='utf8', newline='').write(remainder)

def extract_and_write(f, path):
    if docs:
        cases = extract_docs_cases(path)
    elif f.endswith('.sol'):
        cases = [open(path, mode='r', encoding='utf8', newline='').read()]
    else:
        cases = extract_test_cases(path)
    write_cases(f, cases)

if __name__ == '__main__':
    path = sys.argv[1]
    docs = len(sys.argv) > 2 and sys.argv[2] == 'docs'
    if isfile(path):
        extract_and_write(path, path)
    else:
        for root, subdirs, files in os.walk(path):
            if '_build' in subdirs:
                subdirs.remove('_build')
            if 'compilationTests' in subdirs:
                subdirs.remove('compilationTests')
            for f in files:
                _, tail = split(f)
                if tail == "invalid_utf8_sequence.sol":
                    continue  # ignore the test with broken utf-8 encoding
                path = join(root, f)
                extract_and_write(f, path)
