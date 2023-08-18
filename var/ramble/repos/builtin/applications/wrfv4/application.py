# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *
from ramble.app.builtin.wrfv3 import Wrfv3 as BuiltinWrfv3


class Wrfv4(BuiltinWrfv3):
    '''The Weather Research and Forecasting (WRF) Model is a next-generation
    mesoscale numerical weather prediction system designed for both
    atmospheric research and operational forecasting applications.'''
    name = 'wrfv4'

    # Append to wrfv3 maintainers
    maintainers('dodecatheon')

    # Replace existing default compiler
    purge_attr_vals('default_compilers')
    default_compiler('gcc9', spack_spec='gcc@9.3.0')

    # Clear out software_specs
    purge_attr_vals('software_specs')

    software_spec('intel-mpi', spack_spec="intel-mpi@2018.4.274",
                  compiler='gcc9')

    software_spec('wrfv4',
                  spack_spec="wrf@4.2 build_type=dm+sm compile_type=em_real nesting=basic ~chem ~pnetcdf",
                  compiler='gcc9')

    # Use existing input files with new URLs and SHA256 values
    update_attr_val('inputs', 'CONUS_2p5km',
                    url='https://www2.mmm.ucar.edu/wrf/users/benchmark/v422/v42_bench_conus2.5km.tar.gz',
                    sha256='dcae9965d1873c1c1e34e21ad653179783302b9a13528ac10fab092b998578f6')

    update_attr_val('inputs', 'CONUS_12km',
                    url='https://www2.mmm.ucar.edu/wrf/users/benchmark/v422/v42_bench_conus12km.tar.gz',
                    sha256='6a0e87e3401efddc50539e71e5437fd7a5af9228b64cd4837e739737c3706fc3')

    # New executable
    executable('fix_12km',
               template=[
                   "sed -i -e 's/ start_hour.*/ start_hour                          = 23,/g' namelist.input",
                   "sed -i -e 's/ restart .*/ restart                             = .true.,/g' namelist.input"
               ], use_mpi=False)

    # Update existing workload
    update_attr_val('workloads', 'CONUS_12km',
                    executables=['cleanup', 'copy', 'fix_12km', 'execute'])
