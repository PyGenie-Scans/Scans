#!/usr/bin/env sh

coverage run --source Scans -m doctest doc/source/tutorial.rst
PERCENT=`coverage report | awk '/TOTAL/ {print $6}'`
# coverage report | sed '/TOTAL/'
sed -r "s/-[0-9]+%25-/-${PERCENT}25-/" readme.md > readme.md.tmp
mv readme.md.tmp readme.md
