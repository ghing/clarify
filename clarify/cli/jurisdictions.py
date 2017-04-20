import sys

import six

import clarify

if six.PY2:
    # Use backported Python 3-style csv package so we can write unicode
    from backports import csv
else:
    import csv


def add_parser(subparsers):
    parser = subparsers.add_parser('jurisdictions',
        description="Fetch jurisdictions with results as CSV from from a Clarity system")
    parser.add_argument('results_url',
            help="URL for the main results page for the election")
    parser.add_argument('--level', default='state',
            help="Reporting level of initial page. Default is 'state'.")
    parser.add_argument('--cachedir', default=None,
            help="Location of directory where files will be downloaded. By default, a temporary directory is created")
    parser.set_defaults(func=main)

    return parser


def get_all_jurisdictions(j):
    """Return a flat list of a jurisdiction and its subjurisdictions"""
    jurisdictions = [j]

    for jurisdiction in j.get_subjurisdictions():
        jurisdictions += get_all_jurisdictions(jurisdiction)

    return jurisdictions


def main(args):
    fieldnames = [
        'name',
        'level',
        'url'
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    base_jurisdiction = clarify.Jurisdiction(url=args.results_url,
        level=args.level)

    for jurisdiction in get_all_jurisdictions(base_jurisdiction):
        writer.writerow({
            'name': jurisdiction.name,
            'level': jurisdiction.level,
            'url': jurisdiction.url,
        })
