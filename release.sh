#!/bin/bash

DO_TEST=false

while [[ $# > 0 ]]; do
    case "$1" in
        -t | --test) DO_TEST=true; shift;;
        --) shift; break;;
        *) echo "$0 with wrong args!"; exit 1;;
    esac
done

README_MD="README.md"
README_RST="README.rst"

if [ "$DO_TEST" = true ]; then
    INDEX='testpypi'  # defined in ~/.pypirc index-servers
else
    INDEX='pypi'
fi

# Convert README.md to README.rst using pandoc
if [ `which pandoc` ]; then
    pandoc -f markdown -t rst -o ${README_RST} ${README_MD} && echo "Convert md to rst ok."
else
    echo "pandoc not installed."
fi

# Release
read -p "Release [$INDEX]? (y/n) " RESP
if [ "$RESP" = "y"  ]; then
    echo "Begin to release"
    python setup.py release -r $INDEX
else
    echo "Cancel to release"
fi

# Post process
rm ${README_RST}
rm -rf build dist simiki.egg-info

if [ "$DO_TEST" = false ]; then
    # Add tag to HEAD
    version=`python -m simiki.cli --version | awk {'printf $2'}`
    git tag v${version}
fi
