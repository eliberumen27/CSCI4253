#!/usr/bin/env python
"""mapper.py"""

import re
import sys

# input comes from STDIN (standard input)
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()
    # split the line into URLs found and pattern match using regex
    # We are grouping with parenthesis to extract and only return what's within that
    urls = re.findall('href\s*=\s*"([^""]*)"', line) # Pattern matches on href, optional whitespace, equals, and match anything that IS NOT double quote up to the next "
    # increase counters
    for url in urls:
        # write the results to STDOUT (standard output);
        # what we output here will be the input for the
        # Reduce step, i.e. the input for reducer.py
        #
        # tab-delimited; the trivial word count is 1
        print('%s\t%s' % (url, 1))