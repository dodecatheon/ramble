#!/bin/bash -p
# Define shell function that bootstraps spack to install miniconda3,
# configure miniconda to have the latest version of google-cloud-storage,
# then setup spack to use the centos7 buildcache and treat slurm like
# an external tool instead of building it.
#
# NOTE: if CONDAPKG is set and exported to be "anaconda3" before running this function,
#       spack will install and use anaconda3 instead of miniconda3. Otherwise,
#       miniconda3 is the default.

install_spack () {
  echo "Run this command *ONLY ONCE* to install spack"
  # install spack
  test -v DEVBASE || export DEVBASE=$HOME/dev && \
  mkdir -p $DEVBASE && \
  test -v SPACKBASE || export SPACKBASE=$DEVBASE/spack && \
  test -d $SPACKBASE || {
    echo "installing spack"
    cd $DEVBASE
    git clone -c feature.manyFiles=true https://github.com/spack/spack.git
  }

  echo "Checkout develop branch for spack"
  cd $SPACKBASE
  git fetch --all
  git checkout develop || git checkout -t origin/develop -b develop
  git branch --set-upstream-to=origin/develop
  git pull

  # install $CONDAPKG (via a sub-shell)
  test -v CONDAPKG || export CONDAPKG=miniconda3 && \
  test -v SPACKSETUP || export SPACKSETUP=$SPACKBASE/share/spack/setup-env.sh && \
  test -r $SPACKSETUP && {
    type conda >/dev/null 2>&1 && \
    export CONDABOOTSTRAP=0 || {
      echo "installing $CONDAPKG"
      (
        source $SPACKSETUP
        spack install $CONDAPKG
      )
      export CONDABOOTSTRAP=1
    }
    cd $HOME

    # configure conda package and spack in a sub-shell
    (
      echo "Ensure conda in path before setting up spack and ramble"
      ((CONDABOOTSTRAP == 1)) && export PATH="$(source $SPACKSETUP; spack location -i $CONDAPKG)/bin:$PATH"

      echo "install google-cloud-storage via conda"
      conda install google-cloud-storage
      conda update -y google-cloud-storage
      conda list google-cloud-storage

      echo "Setup spack"
      source $SPACKSETUP

      echo "configure spack for concretizer, buildcache, etc."
      spack config add 'concretizer:targets:host_compatible:false'
      spack mirror add gcs gs://spack/v0.19.0
      spack gpg init
      spack buildcache keys --install --trust

      # Configure spack to know slurm is an external tool:
      echo "configure spack for slurm"
      spack external find -p /usr/local --all --not-buildable
      spack info slurm

      # Configure spack to build under $HOME instead of /tmp
      SPACKCONFIG=~/.spack/config.yaml
      type -r ${SPACKCONFIG} && mv ${SPACKCONFIG} ${SPACKCONFIG}~
      cat > ${SPACKCONFIG} <<-EOF
	config:
	  build_stage:
	    - \$user_cache_path/stage
	    - \$tempdir/\$user/spack-stage
	EOF
    )
  } || {
    echo "$SPACKSETUP not found, problem with git clone or checkout"
    return 1
  }
}
