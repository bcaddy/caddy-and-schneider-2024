#!/usr/bin/env python3
"""
================================================================================
 Written by Robert Caddy.

 This contains the various shared tools that the python scripts will use
================================================================================
"""

import pathlib
import pickle
import subprocess

pickle_filepath = pathlib.Path(__file__).resolve().parent / 'links.pkl'

github_url_root = 'https://github.com/bcaddy/caddy-et-al-2023/blob'

def pickle_dictionary(dictionary, path=pickle_filepath):
    with open(path, 'wb') as file:
        pickle.dump(dictionary, file)

def unpickle_dictionary(path=pickle_filepath):
    if path.exists():
        with open(path, 'rb') as file:
            return pickle.load(file)
    else:
        return {}

def update_plot_entry(key, script_name):
    data = unpickle_dictionary()

    commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    link = f'{github_url_root}/{commit_hash}/{script_name}'

    data[key] = link

    pickle_dictionary(data)

def main():
    dictionary = {'a':1, 'b':2, 'charlie':47, 'test_link':'https://docs.python.org/3/library/pathlib.html'}

    pickle_dictionary(dictionary, pickle_filepath)
    print(unpickle_dictionary(pickle_filepath))


if __name__ == '__main__':
    main()