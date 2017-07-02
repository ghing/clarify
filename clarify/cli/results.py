import errno
import hashlib
from itertools import chain
import logging
import os
import shutil
import sys
import tempfile
from zipfile import ZipFile

import requests
import six

import clarify
from clarify.util import jurisdiction_levels_from_url

if six.PY2:
    # Use backported Python 3-style csv package so we can write unicode
    from backports import csv
else:
    import csv


def makedirs_exist_ok(path):
    """
    Create a directory if it doesn't already exist.

    This is equivalent to `os.makedirs(path,exist_ok=True)` in Python
    3.2+

    """
    try:
        os.makedirs(path)

    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_cache_filename(url):
    return hashlib.md5(url).hexdigest() + ".zip"


def fetch_url(url, cache_dir, override_cache=False):
    path = os.path.join(cache_dir, get_cache_filename(url))

    if os.path.exists(path) and not override_cache:
        return path

    response = requests.get(url, stream=True)

    with open(path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)

    return path


def unzip(path):
    detail_zip = ZipFile(path)
    return detail_zip.open('detail.xml')


def get_results_from_file(f):
    parser = clarify.Parser()
    parser.parse(f)
    return parser.results


def result_as_dict(result, **addl_cols):
    """Return a result as a dictionary suitable for serialization"""
    result_dict = dict(**addl_cols)
    result_dict['office'] = result.contest.text
    # Cols:
    #  county, precinct, office, district, party, candidate, votes, winner (if
    #  it's in the data).

    if result.jurisdiction is not None:
        jurisdiction_key = result.jurisdiction.level
        result_dict[jurisdiction_key] = result.jurisdiction.name

    if result.choice is not None:
        result_dict['candidate'] = result.choice.text
        result_dict['party'] = result.choice.party

    result_dict['votes'] = result.votes
    result_dict['vote_type'] = result.vote_type

    return result_dict


def get_report_urls(jurisdictions):
    return (j.report_url('xml') for j in jurisdictions)


def fetch_urls(urls, cache_dir):
    return (fetch_url(url, cache_dir) for url in urls)


def get_results(paths):
    return chain.from_iterable(get_results_from_file(unzip(path)) for path in paths)


def add_parser(subparsers):
    parser = subparsers.add_parser('results',
        description="Fetch election results as CSV from from a Clarity system")
    parser.add_argument('results_url',
            help="URL for the main results page for the election")
    parser.add_argument('--cachedir', default=None,
            help="Location of directory where files will be downloaded. By default, a temporary directory is created")
    parser.add_argument('--log', default=None)
    parser.set_defaults(func=main)

    return parser


def main(args):
    if args.log is not None:
        numeric_level = getattr(logging, args.log.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError("Invalid log level: {level}".format(
                level=args.log))

        logging.basicConfig(level=numeric_level)

    cache_path = args.cachedir
    temporary_cache_dir = False
    if cache_path is None:
        temporary_cache_dir = True
        cache_path = tempfile.mkdtemp()

    else:
        makedirs_exist_ok(cache_path)

    levels = jurisdiction_levels_from_url(args.results_url)
    lowest_level = levels[-1]['level']
    base_jurisdiction = clarify.Jurisdiction(url=args.results_url,
        level=lowest_level)
    results_iter = get_results(fetch_urls(get_report_urls([base_jurisdiction]),
        cache_path))

    # We want the fields in the output CSV, and their order to match those
    # in the data entry instructions for OpenElex
    # (http://docs.openelections.net/data-entry/#instructions).
    fieldnames = [
        'office',
        'candidate',
        'party',
    ]

    # Now add in the jurisdiction columns.  Unlike the  examples in the
    # docs, we'll also add a state column, useful if you're slamming results
    # into a single database.
    addl_cols = {}
    for level in levels:
        addl_cols[level['level']] = level['name']
        fieldnames.append(level['level'])

    if lowest_level == 'county':
        # URL indicates county, which means we'll have results for each
        # precinct
        fieldnames.append('precinct')


    # Votes go last
    fieldnames += [
        'votes',
        'vote_type',
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for result in results_iter:
        writer.writerow(result_as_dict(result, **addl_cols))

    if temporary_cache_dir:
        # If we created a temporary cache directory, delete it.
        shutil.rmtree(cache_path)
