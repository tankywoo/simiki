#!/bin/bash

README_MD="README.md"
README_RST="README.rst"

# Convert README.md to README.rst using pandoc
if [ `which pandoc` ]; then
    pandoc -f markdown -t rst -o ${README_RST} ${README_MD} && echo "Convert md to rst ok."
else
    echo "pandoc not installed."
fi

# Release
read -p "Release? (y/n) " RESP
if [ "$RESP" = "y"  ]; then
    echo "Begin to release"
    python setup.py release
else
    echo "Cancel to release"
fi

# Post process
rm ${README_RST}
rm -rf build dist simiki.egg-info

# Add tag to HEAD
version=`python -m simiki.cli --version | awk {'printf $2'}`
git tag v${version}
