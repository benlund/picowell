import sys
import json

DebugFile = const('/debug.txt')

def write(str):
    with open(DebugFile, 'w') as f:
        f.write(str)


def write_json(dict):
    write(json.dumps(dict))


def append_exception(e):
    with open(DebugFile, 'a') as f:
        f.write('\n')
        sys.print_exception(e, f)
