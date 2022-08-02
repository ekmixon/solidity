#!/usr/bin/env python3
#
# This script reads C++ or RST source files and writes all
# multi-line strings into individual files.
# This can be used to extract the Solidity test cases
# into files for e.g. fuzz testing as
# scripts/isolate_tests.py test/libsolidity/*

import sys
import re

def extract_test_cases(_path):
    lines = open(_path, mode='rb', encoding='utf8').read().splitlines()

    inside = False
    delimiter = ''
    test = ''

    ctr = 1
    test_name = ''

    for l in lines:
        if inside:
            if l.strip().endswith(f'){delimiter}' + '";'):
                open('%03d_%s.sol' % (ctr, test_name), mode='wb', encoding='utf8').write(test)
                ctr += 1
                inside = False
                test = ''
            else:
                l = re.sub('^\t\t', '', l)
                l = l.replace('\t', '        ')
                test += l + '\n'
        else:
            if m := re.search(r'BOOST_AUTO_TEST_CASE\(([^(]*)\)', l.strip()):
                test_name = m[1]
            if m := re.search(r'R"([^(]*)\($', l.strip()):
                inside = True
                delimiter = m[1]

if __name__ == '__main__':
    extract_test_cases(sys.argv[1])
