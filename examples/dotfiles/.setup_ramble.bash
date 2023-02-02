#!/bin/bash -p
# run this at most one time per login shell
# ** AFTER ** running setup_spack
function setup_ramble () {
  type ramble >/dev/null 2>&1 && \
  echo "Ramble already setup" || {
    type spack >/dev/null 2>&1 && {
      test -v DEVBASE || export DEVBASE=$HOME/dev && \
      test -v RAMBLEBASE || export RAMBLEBASE=$DEVBASE/ramble && \
      test -v RAMBLESETUP || export RAMBLESETUP=$RAMBLEBASE/share/ramble/setup-env.sh && \
      test -r $RAMBLESETUP && source $RAMBLESETUP || \
      echo "Run install_ramble first"
    } || echo "Run setup_spack first"
  }
}
