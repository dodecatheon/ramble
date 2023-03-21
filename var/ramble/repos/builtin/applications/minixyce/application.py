# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.


from ramble.appkit import *


class Minixyce(SpackApplication):
    '''Define miniXyce application'''
    name = 'minixyce'

    tags = ['circuitdesign', 'miniapp', 'minibenchmark', 'mini-benchmark']

    default_compiler('gcc12', base='gcc', version='12.2.0', target='x86_64')

    mpi_library('ompi415', base='openmpi', version='4.1.5',
                variants='+legacylaunchers +pmi +cxx')

    software_spec('minixyce',
                  base='minixyce',
                  version='1.0',
                  compiler='gcc12',
                  variants='+mpi',
                  mpi='ompi415',
                  required=True)

    executable('execute', 'miniXyce.x --circuit {workload_name}.net', use_mpi=True)

    executable('get_simple_network',
               template=['cp {minixyce}/tests/{workload_name}.net {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RC_ladder_network_8',
               template=['perl {minixyce}/tests/RC_ladder.pl 8 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RLC_ladder_network_8',
               template=['perl {minixyce}/tests/RLC_ladder.pl 8 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RC_ladder_network_16',
               template=['perl {minixyce}/tests/RC_ladder.pl 16 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RLC_ladder_network_16',
               template=['perl {minixyce}/tests/RLC_ladder.pl 16 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RC_ladder2_network_8',
               template=['perl {minixyce}/tests/RC_ladder2.pl 8 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RLC_ladder2_network_8',
               template=['perl {minixyce}/tests/RLC_ladder2.pl 8 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RC_ladder2_network_16',
               template=['perl {minixyce}/tests/RC_ladder2.pl 16 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    executable('generate_RLC_ladder2_network_16',
               template=['perl {minixyce}/tests/RLC_ladder2.pl 16 > {experiment_run_dir}/{workload_name}.net'],
               use_mpi=False)

    workload('cir1', executables=['get_simple_network', 'execute'])
    workload('cir2', executables=['get_simple_network', 'execute'])
    workload('cir3', executables=['get_simple_network', 'execute'])
    workload('cir4', executables=['get_simple_network', 'execute'])
    workload('cir5', executables=['get_simple_network', 'execute'])
    workload('cir6', executables=['get_simple_network', 'execute'])
    workload('RC_8', executables=['generate_RC_ladder_network_8', 'execute'])
    workload('RLC_8', executables=['generate_RLC_ladder_network_8', 'execute'])
    workload('RC_16', executables=['generate_RC_ladder_network_16', 'execute'])
    workload('RLC_16', executables=['generate_RLC_ladder_network_16', 'execute'])
    workload('RC_8_2', executables=['generate_RC_ladder2_network_8', 'execute'])
    workload('RLC_8_2', executables=['generate_RLC_ladder2_network_8', 'execute'])
    workload('RC_16_2', executables=['generate_RC_ladder2_network_16', 'execute'])
    workload('RLC_16_2', executables=['generate_RLC_ladder2_network_16', 'execute'])

    log_file = '{experiment_run_dir}/miniXyce.out'

    floating_point_regex = r'[\+\-]*[0-9]*\.*[0-9]+E*[\+\-]*[0-9]*'

    step_count_regex = r'\s*Step\s+(?P<step>[0-9]+).*\s+timestep\s+(?P<timestep>' + floating_point_regex + r')'

    wall_clock_regex = r'\s*Wall clock\s+(?P<wall_clock>[0-9]+\.[0-9]+)'

    figure_of_merit('Timestep', log_file=log_file,
                    fom_regex=step_count_regex,
                    group_name='timestep',
                    units='s', contexts=['step']
                    )

    figure_of_merit('Wall Clock', log_file=log_file,
                    fom_regex=wall_clock_regex,
                    group_name='wall_clock',
                    units='s', contexts=['step']
                    )

    figure_of_merit_context('step',
                            regex=step_count_regex,
                            output_format='{step}')

    step_summary_regex = (r'\s*step:\s+(?P<step>[0-9]+)\s+' +
                          r'(?P<volume>'          + floating_point_regex + r')\s+' +
                          r'(?P<mass>'            + floating_point_regex + r')\s+' +
                          r'(?P<density>'         + floating_point_regex + r')\s+' +
                          r'(?P<pressure>'        + floating_point_regex + r')\s+' +
                          r'(?P<internal_energy>' + floating_point_regex + r')\s+' +
                          r'(?P<kinetic_energy>'  + floating_point_regex + r')\s+' +
                          r'(?P<total_energy>'    + floating_point_regex + r')')

    figure_of_merit('Total step count', log_file=log_file,
                    fom_regex=step_summary_regex,
                    group_name='step',
                    units=''
                    )

    figure_of_merit('Final Kinetic Energy', log_file=log_file,
                    fom_regex=step_summary_regex,
                    group_name='kinetic_energy',
                    units='Joules'
                    )

    figure_of_merit('Total Elapsed Time', log_file=log_file,
                    fom_regex=wall_clock_regex,
                    group_name='wall_clock',
                    units='s'
                    )

    figure_of_merit('First step overhead', log_file=log_file,
                    fom_regex=(r'\s*First step overhead\s+(?P<overhead>' + floating_point_regex + r')'),
                    group_name='overhead',
                    units='s'
                    )
