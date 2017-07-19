#!/usr/bin/env bash

me=`basename "$0"`

if [ "$#" -lt 2 ]; then
  echo "Usage: $me Source_DIR Link_DIR"
  exit 1
fi

# Prepare
src=$1
src_path_name=`basename $src`
src_parent=$(dirname $src)
dest=$2
mkdir -p $dest
current=${PWD}

# Hardlink recursively
echo "Create hardlink for diretroy $1 TO: $2"
relative_to_src=`realpath --relative-to=src_parent $2`
cd $src_parent
pax -rwlpe $src_path_name $dest
cd $current_dir
