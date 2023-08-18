# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

from ramble.appkit import *
from ramble.app.builtin.hpl import Hpl as BuiltinHpl


class IntelHpl(BuiltinHpl):
    '''Run HPL application using Intel MKL optimized binary from intel-oneapi-mpi package'''
    name = 'intel-hpl'

    # Replace existing maintainers
    purge_attr('maintainers')
    maintainers('dodecatheon')

    # Append to existing tags
    tags('optimized', 'intel', 'mkl')

    # Add imkl_2023p1 as a software_spec and required package,
    # while removing hpl from both
    software_spec('imkl_2023p1', spack_spec='intel-oneapi-mkl@2023.1.0 threads=openmp')
    remove_attr_val('software_specs', 'hpl')
    purge_attr('required_packages')
    required_package('intel-oneapi-mkl')

    executable('execute',
               '{intel-oneapi-mkl}/mkl/latest/benchmarks/mp_linpack/xhpl_intel64_dynamic',
               use_mpi=True)

    # Redefine default workload variable bcast to 6 for the MKL-optimized
    # calculator workload
    update_attr_val('workload_variables',
                    'bcast',
                    keys='calc*',
                    default='6',
                    description='BCAST for Intel MKL optimized calculator')
