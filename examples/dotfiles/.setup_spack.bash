#!/bin/bash -p
# run this at most one time per login shell
function setup_spack () {
  type spack >/dev/null 2>&1 && \
  echo "Spack already setup" || {
    test -v DEVBASE || export DEVBASE=$HOME/dev && \
    test -v SPACKBASE || export SPACKBASE=$DEVBASE/spack && \
    test -v CONDAPKG || export CONDAPKG=miniconda3 && \
    test -v SPACKSETUP || export SPACKSETUP=$SPACKBASE/share/spack/setup-env.sh && \
    test -r $SPACKSETUP && {
      type conda >/dev/null 2>&1 || \
      export PATH="$(source $SPACKSETUP; spack location -i $CONDAPKG)/bin:$PATH" && \
      source $SPACKSETUP
    } || echo "Run install_spack first"
  }
}
