#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Loads and returns the link to the requested key
================================================================================
"""

import shared_tools
import argparse


def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', help='The key to the link to load')
    args = parser.parse_args()

    if args.key:
        key = args.key
    else:
        print(f'ERROR: A KEY WAS NOT PROVIDED')
        exit()

    print(shared_tools.unpickle_dictionary()[key])


if __name__ == '__main__':
    main()