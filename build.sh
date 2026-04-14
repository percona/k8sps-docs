#!/bin/bash
# This script is used for building a themed site to preview on render.com
# Preview URL: https://percona-postgresql-operator.onrender.com

#for filename in docs/ReleaseNotes/*.md; do
#  mv "$filename" "$filename.bak"
#  echo "m4_changequote({{,}})" > "$filename"
#  echo "m4_patsubst(" >> "$filename"
#  cat "$filename.bak" >> "$filename"  
#  echo ",{{:jirabug:\`\\(.*?\\)\`}},{{[\\1](https:\\/\\/jira.percona.com/browse\\/\\1)}})" >> "$filename"
#  m4 -P "$filename.bak" > "$filename.m4"
#done

python -m pip install --upgrade pip
pip install wheel
pip install yq


# This command extracts the value of the 'release' key from variables.yml and stores it in the 'version' variable.
version=$(yq e '.release' < variables.yml)

mike deploy $version
mike set-default $version

#for filename in docs/ReleaseNotes/*.md; do
#  mv "$filename.bak" "$filename"
#done
