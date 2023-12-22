#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 Loads and returns the link to the requested key
================================================================================
"""

import pickle
import argparse
import pathlib


def main():
    # Check for CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('key', help='The key to the link to load')
    args = parser.parse_args()

    path = pathlib.Path(__file__).resolve().parent.parent / 'python' / 'links.pkl'
    with open(path, 'rb') as file:
        links = pickle.load(file)

    link = f'\href{{{links[args.key]}}}{{\img{{../latex-src/github.png}}}}'

    print(link)


if __name__ == '__main__':
    main()