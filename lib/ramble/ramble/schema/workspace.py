# Copyright 2022-2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# https://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or https://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

"""Schema for workspace.yaml configuration file.

.. literalinclude:: _ramble_root/lib/ramble/ramble/schema/workspace.py
   :lines: 12-
"""  # noqa E501

from llnl.util.lang import union_dicts

import spack.schema.env
import ramble.schema.applications
import ramble.schema.merged
import ramble.schema.licenses

env_properties = spack.schema.env.schema['patternProperties']
spec_properties = env_properties['^env|spack$']

applications_properties = ramble.schema.applications.properties['applications']
app_addProps = applications_properties['additionalProperties']

keys = ('ramble', 'workspace')

#: Properties for inclusion in other schemas
properties = {
    'ramble': {
        'type': 'object',
        'default': {},
        'properties': union_dicts(
            ramble.schema.merged.properties,
            {
                'mpi': {
                    'type': 'object',
                    'properties': {
                        'command': {
                            'type': 'string'
                        },
                        'args': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'default': []
                        }
                    },
                    'additionalProperties': False,
                    'default': {},
                },
                'batch': {
                    'type': 'object',
                    'properties': {
                        'submit': {
                            'type': 'string'
                        },
                    },
                    'additionalProperties': False,
                    'default': {}
                },
                'include': {
                    'type': 'array',
                    'default': [],
                    'items': {'type': 'string'},
                },
                'env-vars': ramble.schema.licenses.env_var_actions,
                'application_directories': {
                    'type': 'array',
                    'default': [],
                    'items': {
                        'type': 'string'
                    }
                }
            }
        ),
        'additionalProperties': False,
    },
    # TODO (dwj): Remove when non-config spack is removed
    # DEPRECATED
    'spack': ramble.schema.spack.properties['spack']  # To support non-config spack
}


#: Full schema with metadata
schema = {
    '$schema': 'http://json-schema.org/schema#',
    'title': 'Ramble workspace configuration file schema',
    'type': 'object',
    'additionalProperties': ramble.schema.spack.properties,
    'properties': properties,
}
