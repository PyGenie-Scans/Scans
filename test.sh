#!/usr/bin/env sh

set -e

coverage run --source Scans -m doctest doc/source/instrument.rst doc/source/tutorial.rst
PERCENT=`coverage report | awk '/TOTAL/ {print $4}'`
# coverage report | sed '/TOTAL/'
sed -r "s/-[0-9]+%25-/-${PERCENT}25-/" readme.md > readme.md.tmp
mv readme.md.tmp readme.md
coverage html
