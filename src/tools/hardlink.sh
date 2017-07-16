#!/usr/bin/env bash

me=`basename "$0"`

echo $? $1 $2
if [ "$#" -lt 2 ]; then
  echo "Usage: $me Source_DIR Link_DIR"
  exit 1
fi

echo "Create hardlink for diretroy $1"
mkdir $2
pax -rwlpe $1 $2
