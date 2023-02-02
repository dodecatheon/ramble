#!/bin/bash -p
#
# Define a function that is run ONCE to install ramble

install_ramble () {
  echo "Run this command *ONLY ONCE* to install ramble"
  # install spack
  test -v DEVBASE && test -d $DEVBASE || {
    export DEVBASE=$HOME/dev
    echo "Defining DEVBASE=$DEVBASE and ensuring it exists"
    mkdir -p $DEVBASE
  }

  type spack >/dev/null 2>&1 && {
    type ramble >/dev/null 2>&1 || {
      test -v RAMBLEBASE || export RAMBLEBASE=$DEVBASE/ramble && \
      test -d $RAMBLEBASE && \
      {
        cd $RAMBLEBASE
        git fetch --all
        git checkout develop
        git branch --set-upstream-to=origin/develop
        git pull
      } || {
        git clone -c feature.manyFiles=true https://github.com/GoogleCloudPlatform/ramble.git
        cd $RAMBLEBASE
        git fetch --all
        git checkout develop || git checkout -t origin/develop -b develop
        git branch --set-upstream-to=origin/develop
        git pull
      }
    } || echo "Ramble already in path"
  } || \
  {
    echo "Spack must be installed and setup before installing ramble"
    return 1
  }
}
