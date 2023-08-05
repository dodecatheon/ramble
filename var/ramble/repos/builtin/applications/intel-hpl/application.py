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
    '''Test new description'''
    name = 'intel-hpl'

    purge_attribute('maintainers')
    maintainers('dodecatheon')

    purge_attribute('tags')
    tags('optimized', 'intel', 'mkl')

    software_spec('imkl_2023p1', spack_spec='intel-oneapi-mkl@2023.1.0 threads=openmp')

    purge_attribute('required_packages')

    remove_attribute('software_specs', 'hpl')

    executable('execute',
               '{intel-oneapi-mkl}/mkl/latest/benchmarks/mp_linpack/xhpl_intel64_dynamic',
               use_mpi=True)

    # Redefine default workload variable bcast to 6 for the MKL-optimized case
    workload_variable('bcast',
                      default='6',
                      description='BCAST for Intel MKL optimized calculator',
                      workloads=['calculator'])
