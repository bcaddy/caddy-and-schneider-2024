#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Loads and returns the link to the requested key
================================================================================
"""

from shared_tools import unpickle_dictionary
import argparse


def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('key', help='The key to the link to load')
    args = parser.parse_args()

    link = f'\href{{{unpickle_dictionary()[args.key]}}}{{\img{{../assets/github.png}}}}'

    print(link)


if __name__ == '__main__':
    main()