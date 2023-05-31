#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 This contains the various shared tools that the python scripts will use
================================================================================
"""

import pathlib
import pickle

pickle_filepath = pathlib.Path(__file__).resolve().parent / 'links.pkl'

def pickle_dictionary(dictionary, path=pickle_filepath):
    with open(path, 'wb') as file:
        pickle.dump(dictionary, file)

def unpickle_dictionary(path=pickle_filepath):
    with open(path, 'rb') as file:
        dictionary = pickle.load(file)
    return dictionary

def main():
    dictionary = {'a':1, 'b':2, 'charlie':47, 'test_link':'https://docs.python.org/3/library/pathlib.html'}

    pickle_dictionary(dictionary, pickle_filepath)
    print(unpickle_dictionary(pickle_filepath))


if __name__ == '__main__':
    main()