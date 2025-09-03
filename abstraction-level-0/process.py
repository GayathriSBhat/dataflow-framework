# This program reads lines from standard input, converts them to uppercase, and prints them to standard output
'''For simplicity, it does not handle file input/output or different modes and does not use any external libraries.'''
import sys

for line in sys.stdin:
    line = line.strip()
    line = line.upper()
    print(line)


''' Example usage:
    $ echo "hello world" | python3 uppercase_stream.py'''