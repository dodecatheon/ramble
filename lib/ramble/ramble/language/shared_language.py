# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import llnl.util.tty as tty

import ramble.language.language_base
import ramble.language.language_helpers
import ramble.success_criteria
from ramble.language.language_base import DirectiveError
from copy import deepcopy
from fnmatch import fnmatch


"""This module contains directives directives that are shared between multiple object types

Directives are functions that can be called inside an object
definition to modify the object, for example:

    .. code-block:: python

      class Gromacs(SpackApplication):
          # Required package directive
          required_package('zlib')

In the above example, 'required_package' is a ramble directive

Directives defined in this module are used by multiple object types, which
inherit from the SharedMeta class.
"""


class SharedMeta(ramble.language.language_base.DirectiveMeta):
    _directive_names = set()
    _directives_to_be_executed = []


# shared_directive = ramble.language.language_base.DirectiveMeta.directive
shared_directive = SharedMeta.directive


@shared_directive('archive_patterns')
def archive_pattern(pattern):
    """Adds a file pattern to be archived in addition to figure of merit logs

    Defines a new file pattern that will be archived during workspace archival.
    Archival will only happen for files that match the pattern when archival
    is being performed.

    Args:
      pattern: Pattern that refers to files to archive
    """

    def _execute_archive_pattern(obj):
        obj.archive_patterns[pattern] = pattern

    return _execute_archive_pattern


@shared_directive('figure_of_merit_contexts')
def figure_of_merit_context(name, regex, output_format):
    """Defines a context for figures of merit

    Defines a new context to contain figures of merit.

    Args:
      name: High level name of the context. Can be referred to in
            the figure of merit
      regex: Regular expression, using group names, to match a context.
      output_format: String, using python keywords {group_name} to extract
                     group names from context regular expression.
    """

    def _execute_figure_of_merit_context(obj):
        obj.figure_of_merit_contexts[name] = {
            'regex': regex,
            'output_format': output_format
        }

    return _execute_figure_of_merit_context


@shared_directive('figures_of_merit')
def figure_of_merit(name, fom_regex, group_name, log_file='{log_file}', units='',
                    contexts=[]):
    """Adds a figure of merit to track for this object

    Defines a new figure of merit.

    Args:
      name: High level name of the figure of merit
      log_file: File the figure of merit can be extracted from
      fom_regex: A regular expression using named groups to extract the FOM
      group_name: The name of the group that the FOM should be pulled from
      units: The units associated with the FOM
    """

    def _execute_figure_of_merit(obj):
        obj.figures_of_merit[name] = {
            'log_file': log_file,
            'regex': fom_regex,
            'group_name': group_name,
            'units': units,
            'contexts': contexts
        }

    return _execute_figure_of_merit


@shared_directive('default_compilers')
def default_compiler(name, spack_spec, compiler_spec=None, compiler=None):
    """Defines the default compiler that will be used with this object

    Adds a new compiler spec to this object. Software specs should
    reference a compiler that has been added.
    """

    def _execute_default_compiler(obj):
        if hasattr(obj, 'uses_spack') and getattr(obj, 'uses_spack'):
            obj.default_compilers[name] = {
                'spack_spec': spack_spec,
                'compiler_spec': compiler_spec,
                'compiler': compiler
            }

    return _execute_default_compiler


@shared_directive('software_specs')
def software_spec(name, spack_spec, compiler_spec=None, compiler=None):
    """Defines a new software spec needed for this object.

    Adds a new software spec (for spack to use) that this object
    needs to execute properly.

    Only adds specs to object that use spack.

    Specs can be described as an mpi spec, which means they
    will depend on the MPI library within the resulting spack
    environment.
    """

    def _execute_software_spec(obj):
        if hasattr(obj, 'uses_spack') and getattr(obj, 'uses_spack'):

            # Define the spec
            obj.software_specs[name] = {
                'spack_spec': spack_spec,
                'compiler_spec': compiler_spec,
                'compiler': compiler
            }

    return _execute_software_spec


@shared_directive('package_manager_configs')
def package_manager_config(name, config, **kwargs):
    """Defines a config option to set within a package manager

    Define a new config which will be passed to a package manager. The
    resulting experiment instance will pass the config to the package manager,
    which will control the logic of applying it.
    """

    def _execute_package_manager_config(obj):
        obj.package_manager_configs[name] = config

    return _execute_package_manager_config


@shared_directive('required_packages')
def required_package(name):
    """Defines a new spack package that is required for this object
    to function properly.
    """

    def _execute_required_package(obj):
        obj.required_packages[name] = True

    return _execute_required_package


@shared_directive('success_criteria')
def success_criteria(name, mode, match=None, file='{log_file}',
                     fom_name=None, fom_context='null', formula=None):
    """Defines a success criteria used by experiments of this object

    Adds a new success criteria to this object definition.

    These will be checked during the analyze step to see if a job exited properly.

    Arguments:
      name: The name of this success criteria
      mode: The type of success criteria that will be validated
            Valid values are: 'string', 'application_function', and 'fom_comparison'
      match: For mode='string'. Value to check indicate success (if found, it
             would mark success)
      file: For mode='string'. File success criteria should be located in
      fom_name: For mode='fom_comparison'. Name of fom for a criteria.
                Accepts globbing.
      fom_context: For mode='fom_comparison'. Context the fom is contained
                   in. Accepts globbing.
      formula: For mode='fom_comparison'. Formula to use to evaluate success.
               '{value}' keyword is set as the value of the FOM.
    """

    def _execute_success_criteria(obj):
        valid_modes = ramble.success_criteria.SuccessCriteria._valid_modes
        if mode not in valid_modes:
            tty.die(f'Mode {mode} is not valid. Valid values are {valid_modes}')

        obj.success_criteria[name] = {
            'mode': mode,
            'match': match,
            'file': file,
            'fom_name': fom_name,
            'fom_context': fom_context,
            'formula': formula
        }

    return _execute_success_criteria


@shared_directive('builtins')
def register_builtin(name, required=True, injection_method='prepend'):
    """Register a builtin

    Builtins are methods that return lists of strings. These methods represent
    a way to write python code to generate executables for building up
    workloads.

    Manual injection of a builtins can be performed through modifying the
    execution order in the internals config section.

    Modifier builtins are named:
    `modifier_builtin::modifier_name::method_name`.

    Application modifiers are named:
    `builtin::method_name`

    As an example, if the following builtin was defined:

    .. code-block:: python

      register_builtin('example_builtin', required=True)
      def example_builtin(self):
        ...

    Its fully qualified name would be:
    * `modifier_builtin::test-modifier::example_builtin` when defined in a
    modifier named `test-modifier`
    * `builtin::example_builtin` when defined in an application

    The 'required' attribute marks a builtin as required for all workloads. This
    will ensure the builtin is added to the workload if it is not explicitly
    added. If required builtins are not explicitly added to a workload, they
    are injected  into the list of executables, based on the injection_method
    attribute.

    The 'injection_method' attribute controls where the builtin will be
    injected into the executable list.
    Options are:
    - 'prepend' -- This builtin will be injected at the beginning of the executable list
    - 'append' -- This builtin will be injected at the end of the executable list
    """
    supported_injection_methods = ['prepend', 'append']

    def _store_builtin(obj):
        if injection_method not in supported_injection_methods:
            raise ramble.language.language_base.DirectiveError(
                f'Object {obj.name} has an invalid '
                f'injection method of {injection_method}.\n'
                f'Valid methods are {str(supported_injection_methods)}'
            )

        builtin_name = obj._builtin_name.format(obj_name=obj.name, name=name)

        obj.builtins[builtin_name] = {'name': name,
                                      'required': required,
                                      'injection_method': injection_method}
    return _store_builtin


@shared_directive(dicts=())
def maintainers(*names: str):
    """Add a new maintainer directive, to specify maintainers in a declarative way.

    Args:
        names: GitHub username for the maintainer
    """

    def _execute_maintainer(obj):
        maintainers_from_base = getattr(obj, "maintainers", [])
        # Here it is essential to copy, otherwise we might add to an empty list in the parent
        obj.maintainers = list(sorted(set(maintainers_from_base + list(names))))

    return _execute_maintainer


@shared_directive(dicts=())
def tags(*values: str):
    """Add a new tag directive, to specify tags in a declarative way.

    Args:
        values: Value to mark as a tag
    """

    def _execute_tag(obj):
        tags_from_base = getattr(obj, "tags", [])
        # Here it is essential to copy, otherwise we might add to an empty list in the parent
        obj.tags = list(sorted(set(tags_from_base + list(values))))

    return _execute_tag


# Internal utility function
def _check_attrs(obj, message, *args):
    for arg in args:
        if not hasattr(obj, arg):
            raise AttributeError(message +
                                 f" does not contain attribute {arg}")


@shared_directive(dicts=())
def purge_attr_vals(attr_name):
    """Purges all elements of attribute container attr_name in object obj."""
    def _execute_purge_attr_vals(obj):

        _check_attrs(obj, "Object", attr_name)

        attr_obj = getattr(obj, attr_name)

        _check_attrs(attr_obj,
                     f"Attribute container {attr_name}",
                     'clear')

        attr_obj.clear()

    return _execute_purge_attr_vals


# Internal utility function
def _remove_or_pop_item(obj, message, name):
    """Remove or pop item name (with glob matching) from obj"""

    _check_attrs(obj,
                 f"{message}",
                 '__iter__')

    if getattr(obj, 'remove', False):
        remove_function = obj.remove
    elif getattr(obj, 'pop', False):
        remove_function = obj.pop
    else:
        raise AttributeError("No remove or pop " +
                             f"methods available for {message}")

    globmatched_keys = [k for k in obj if fnmatch(k, name)]
    if len(globmatched_keys) > 0:
        for k in globmatched_keys:
            remove_function(k)
    else:
        raise DirectiveError("{message}[{name}] not found")


@shared_directive(dicts=())
def remove_attr_val(attr_name, name, keys=None):
    """Remove components glob-matching 'name' from attribute container attr_name,
    optionally within all keys glob-matching expression 'keys' in attribute
    'attr_name'.

    For example,

    remove_attr_val('workload_variables',
                    '*time*',
                    keys='*motor')

    will remove all workload_variables with 'time' in their name from workloads ending
    in 'motor'."""
    def _execute_remove_attr_val(obj):
        _check_attrs(obj, "Object", attr_name)

        attr_obj = getattr(obj, attr_name)

        if keys:
            _check_attrs(attr_obj,
                         f"{attr_name}",
                         '__iter__', '__getitem__')

            globmatched_keys = [k for k in attr_obj if fnmatch(k, keys)]
            if len(globmatched_keys) > 0:
                for k in globmatched_keys:
                    _remove_or_pop_item(attr_obj[k],
                                        f"{attr_name}[{k}]",
                                        name)
            else:
                raise DirectiveError(f"{attr_name}[{keys}] not found")
        else:
            _remove_or_pop_item(attr_obj, attr_name, name)

    return _execute_remove_attr_val


# Internal utility function
def _update_items(obj_val, message, name, **kwargs):
    #
    # Duck-type for iteration and [] indexing
    #
    _check_attrs(obj_val,
                 message,
                 '__iter__', '__getitem__')

    # Assume len(kwargs) > 0:
    globmatched_keys = [key for key in obj_val if fnmatch(key, name)]
    if len(globmatched_keys) > 0:
        for key in globmatched_keys:
            update_obj = obj_val[key]
            update_obj_name = f"{message}[{key}]"
            _check_attrs(update_obj,
                         update_obj_name,
                         'items')
            # Verify that any replacement values
            # in kwargs are of the same type as what they
            # are replacing
            for k, v in update_obj.items():
                if k in kwargs:
                    if not isinstance(kwargs[k], type(v)):
                        raise DirectiveError("Replacement value type for" +
                                             update_obj_name +
                                             " does not match type of existing value")
            for k, v in kwargs.items():
                # Use a copy to avoid issues with lists, etc.
                update_obj[k] = deepcopy(v)
    else:
        raise DirectiveError(f"{message}[{name}] not found")


# Internal utility function
def _excluded_attrs(name, message, *args):
    if name in args:
        raise DirectiveError(message)


@shared_directive(dicts=())
def update_attr_val(attr_name, name, keys=None, **kwargs):
    """Update attr_name[name] with kwargs, or attr_name[keys][name]
    if keys are provided. Both name and keys use glob matching."""
    def _execute_update_attr_val(obj):
        _excluded_attrs(attr_name,
                        f"Attribute {attr_name} cannot be " +
                        "updated using generic update_attribute",
                        'tags',
                        'maintainers')

        _check_attrs(obj, "Object", attr_name)

        if len(kwargs) > 0:
            attr_obj = getattr(obj, attr_name)
            if keys:
                _check_attrs(attr_obj,
                             attr_name,
                             '__iter__', '__getitem__')
                globmatched_keys = [key for key in attr_obj if fnmatch(key, keys)]
                if len(globmatched_keys) > 0:
                    for key in globmatched_keys:
                        _update_items(attr_obj[key],
                                      f"{attr_name}[{key}]",
                                      name,
                                      **kwargs)
                else:
                    raise DirectiveError(f"{attr_name}[{keys}] not found")
            else:
                _update_items(attr_obj,
                              f"{attr_name}",
                              name,
                              **kwargs)
        else:
            raise DirectiveError("No kwargs provided for update_attr_val")

    return _execute_update_attr_val


# Internal utility function
def _copy_item(obj, obj_name, name):
    """copy obj[name] to new_obj"""
    _check_attrs(obj, obj_name, '__contains__', '__getitem__')
    # New thing doesn't have to be a dict, but it usually is
    # so just call it that
    new_dict = {}
    if name in obj:
        new_dict = deepcopy(obj[name])
    else:
        raise DirectiveError(f"{obj_name}[{name}] not found")

    return new_dict


# Internal utility function
def _create_item(obj, message, newname, new_dict):
    _check_attrs(obj, message, '__getitem__')
    obj[newname] = deepcopy(new_dict)


@shared_directive(dicts=())
def copy_attr_val(attr_name, name, newname, from_key=None, to_keys='*'):
    """Copy component name in attribute attr_name to newname"""
    def _execute_copy_attr_val(obj):
        _check_attrs(obj, "Object", attr_name)

        attr_obj = getattr(obj, attr_name)

        if from_key:
            _check_attrs(attr_obj, attr_name,
                         '__contains__', '__getitem__', '__iter__')

            if from_key in attr_obj:
                new_dict = _copy_item(attr_obj[from_key],
                                      f"{attr_name}[{from_key}]",
                                      name)

                globmatched_keys = [key for key in attr_obj if fnmatch(key, to_keys)]
                if len(globmatched_keys) > 0:
                    for key in globmatched_keys:
                        _create_item(attr_obj[key],
                                     f"{attr_name}[{key}]",
                                     newname, new_dict)
                else:
                    raise DirectiveError(f"{attr_name}[{to_keys}] not found")
            else:
                raise DirectiveError(f"{attr_name}[{from_key}] not found")
        else:
            new_dict = _copy_item(attr_obj, attr_name, name)
            _create_item(attr_obj, attr_name, newname, new_dict)

    return _execute_copy_attr_val
