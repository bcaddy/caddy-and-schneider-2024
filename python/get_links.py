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
    parser.add_argument('key', help='The key to the link to load')
    parser.add_argument('text', help='The key to the link to load')
    args = parser.parse_args()

    link = f'\href{{{shared_tools.unpickle_dictionary()[args.key]}}}{{{args.text}}}'

    print(link)


if __name__ == '__main__':
    main()