# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.
"""Perform tests of the Application class"""

import pytest


@pytest.mark.parametrize('app', [
    'basic', 'basic-inherited', 'input-test', 'interleved-env-vars',
    'register-builtin'
])
def test_app_features(mutable_mock_repo, app):
    app_inst = mutable_mock_repo.get(app)
    assert hasattr(app_inst, 'workloads')
    assert hasattr(app_inst, 'executables')
    assert hasattr(app_inst, 'figures_of_merit')
    assert hasattr(app_inst, 'inputs')
    assert hasattr(app_inst, 'default_compilers')
    assert hasattr(app_inst, 'software_specs')
    assert hasattr(app_inst, 'required_packages')
    assert hasattr(app_inst, 'workload_variables')
    assert hasattr(app_inst, 'builtins')


def test_basic_app(mutable_mock_repo):
    basic_inst = mutable_mock_repo.get('basic')
    assert 'foo' in basic_inst.executables
    assert basic_inst.executables['foo']['template'] == 'bar'
    assert not basic_inst.executables['foo']['mpi']
    assert 'bar' in basic_inst.executables
    assert basic_inst.executables['bar']['template'] == 'baz'
    assert basic_inst.executables['bar']['mpi']

    assert 'test_wl' in basic_inst.workloads
    assert basic_inst.workloads['test_wl']['executables'] == ['builtin::env_vars', 'foo']
    assert basic_inst.workloads['test_wl']['inputs'] == ['input']
    assert 'test_wl2' in basic_inst.workloads
    assert basic_inst.workloads['test_wl2']['executables'] == ['builtin::env_vars', 'bar']
    assert basic_inst.workloads['test_wl2']['inputs'] == ['input']

    assert 'test_fom' in basic_inst.figures_of_merit
    fom_conf = basic_inst.figures_of_merit['test_fom']
    assert fom_conf['log_file'] == 'log_file'
    assert fom_conf['regex'] == \
        r'(?P<test>[0-9]+\.[0-9]+).*seconds.*'  # noqa: W605
    assert fom_conf['group_name'] == 'test'
    assert fom_conf['units'] == 's'

    assert 'input' in basic_inst.inputs
    assert basic_inst.inputs['input']['url'] == \
        'file:///tmp/test_file.log'
    assert basic_inst.inputs['input']['description'] == \
        'Not a file'

    assert 'test_wl' in basic_inst.workload_variables
    assert 'my_var' in basic_inst.workload_variables['test_wl']
    assert basic_inst.workload_variables['test_wl']['my_var']['default'] == \
        '1.0'

    assert basic_inst.workload_variables['test_wl']['my_var']['description'] \
        == 'Example var'


def test_env_var_set_command_gen(mutable_mock_repo):
    basic_inst = mutable_mock_repo.get('basic')

    tests = {
        'var1': 'val1',
        'var2': 'val2'
    }

    answer = [
        'export var1=val1;',
        'export var2=val2;'
    ]

    out_cmds, _ = basic_inst._get_env_set_commands(tests, set())
    for cmd in answer:
        assert cmd in out_cmds


def test_env_var_append_command_gen(mutable_mock_repo):
    basic_inst = mutable_mock_repo.get('basic')

    tests = [
        {
            'var-separator': ',',
            'vars': {
                'var1': 'val1',
                'var2': 'val2'
            },
            'paths': {
                'path1': 'path1',
                'path2': 'path2'
            }
        },
        {
            'var-separator': ',',
            'vars': {
                'var1': 'val2',
                'var2': 'val1'
            },
        }
    ]

    answer = [
        'export var1="${var1},val1,val2";',
        'export var2="${var2},val2,val1";',
        'export path1="${path1}:path1";',
        'export path2="${path2}:path2";'
    ]

    out_cmds, _ = basic_inst._get_env_append_commands(tests, set())
    for cmd in answer:
        assert cmd in out_cmds


def test_env_var_prepend_command_gen(mutable_mock_repo):
    basic_inst = mutable_mock_repo.get('basic')

    tests = [
        {
            'paths': {
                'path1': 'path1',
                'path2': 'path2'
            }
        },
        {
            'paths': {
                'path1': 'path2',
                'path2': 'path1'
            }
        }
    ]

    answer = [
        'export path1="path2:path1:${path1}";',
        'export path2="path1:path2:${path2}";'
    ]

    out_cmds, _ = basic_inst._get_env_prepend_commands(tests, set())
    for cmd in answer:
        assert cmd in out_cmds


def test_env_var_unset_command_gen(mutable_mock_repo):
    basic_inst = mutable_mock_repo.get('basic')

    tests = [
        'var1',
        'var2'
    ]

    answer = [
        'unset var1;',
        'unset var2;'
    ]

    out_cmds, _ = basic_inst._get_env_unset_commands(tests, set())
    for cmd in answer:
        assert cmd in out_cmds


@pytest.mark.parametrize('app_name', ['basic', 'zlib'])
def test_application_copy_is_deep(mutable_mock_repo, app_name):
    src_inst = mutable_mock_repo.get(app_name)

    defined_variables = {
        'test_var1': 'test_val1',
        'test_var2': 'test_val2'
    }

    defined_env_vars = {
        'set': {
            'SET_ENV_VAR': 'TEST'
        },
        'unset': [
            'UNSET_ENV_VAR'
        ],
        'append': [
            {
                'var-separator': ',',
                'vars': {
                    'APPEND_VAR': 'APPEND_TEST'
                }
            }
        ],
        'prepend': [
            {
                'var-separator': ',',
                'vars': {
                    'PREPEND_VAR': 'PREPEND_TEST'
                }
            }
        ]
    }

    defined_internals = {
        'custom_executables': {
            'test_exec': {
                'templates': [
                    'test_exec'
                ],
                'use_mpi': False,
                'redirect': '{log_file}'
            }
        }
    }

    src_inst.set_variables(defined_variables, None)
    src_inst.set_env_variable_sets(defined_env_vars)
    src_inst.set_internals(defined_internals)

    copy_inst = src_inst.copy()

    test_attrs = ['_setup_phases', '_analyze_phases', '_archive_phases',
                  '_mirror_phases']

    # Test Phases
    for attr in test_attrs:
        assert getattr(copy_inst, attr) == getattr(src_inst, attr)

    # Test variables
    for var, val in src_inst.variables.items():
        assert var in copy_inst.variables.keys()
        assert copy_inst.variables[var] == val

    # Test env-vars
    for var_set in src_inst._env_variable_sets.keys():
        assert var_set in copy_inst._env_variable_sets.keys()
        # Test set sets
        if var_set == 'set':
            for var, val in src_inst._env_variable_sets[var_set].items():
                assert var in copy_inst._env_variable_sets[var_set]
                assert copy_inst._env_variable_sets[var_set][var] == val
        elif var_set == 'append' or var_set == 'prepend':
            for idx, set_group in enumerate(src_inst._env_variable_sets[var_set]):
                if 'var-separator' in set_group:
                    assert 'var-separator' in copy_inst._env_variable_sets[var_set][idx]
                    assert copy_inst._env_variable_sets[var_set][idx]['var-separator'] == \
                           set_group['var-separator']
                if 'vars' in set_group:
                    assert 'vars' in copy_inst._env_variable_sets[var_set][idx]
                    for var, val in set_group['vars'].items():
                        assert var in copy_inst._env_variable_sets[var_set][idx]['vars']
                        assert copy_inst._env_variable_sets[var_set][idx]['vars'][var] == val
        elif var_set == 'unset':
            for var in src_inst._env_variable_sets[var_set]:
                assert var in copy_inst._env_variable_sets[var_set]

    # Test internals:
    for internal, conf in src_inst.internals.items():
        assert internal in copy_inst.internals
        if internal == 'custom_executables':
            for exec_name, exec_conf in conf.items():
                assert exec_name in copy_inst.internals[internal]
                for option, value in exec_conf.items():
                    assert option in copy_inst.internals[internal][exec_name]
                    assert copy_inst.internals[internal][exec_name][option] == value


@pytest.mark.parametrize('app', [
    'basic', 'basic-inherited', 'input-test', 'interleved-env-vars',
    'register-builtin'
])
def test_required_builtins(mutable_mock_repo, app):
    app_inst = mutable_mock_repo.get(app)

    required_builtins = []
    for builtin, conf in app_inst.builtins.items():
        if conf[app_inst._builtin_required_key]:
            required_builtins.append(builtin)

    for workload, wl_conf in app_inst.workloads.items():
        if app_inst._workload_exec_key in wl_conf:
            for builtin in required_builtins:
                assert builtin in wl_conf[app_inst._workload_exec_key]


def test_register_builtin_app(mutable_mock_repo):
    app_inst = mutable_mock_repo.get('register-builtin')

    required_builtins = []
    excluded_builtins = []
    for builtin, conf in app_inst.builtins.items():
        if conf[app_inst._builtin_required_key]:
            required_builtins.append(builtin)
        else:
            excluded_builtins.append(builtin)

    for workload, wl_conf in app_inst.workloads.items():
        if app_inst._workload_exec_key in wl_conf:
            for builtin in required_builtins:
                assert builtin in wl_conf[app_inst._workload_exec_key]
            for builtin in excluded_builtins:
                assert builtin not in wl_conf[app_inst._workload_exec_key]
