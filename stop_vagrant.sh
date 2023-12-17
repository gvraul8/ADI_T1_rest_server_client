#!/bin/bash

if ! vagrant status | grep "running"; then
  echo "The Vagrant machine is not running."
  exit 1
fi

export BLOB_STORAGE_FOLDER=$BLOB_STORAGE_FOLDER vagrant halt
