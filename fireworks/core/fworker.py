#!/usr/bin/env python

"""
This module contains classes relevant for a FireWorker (worker computing resource)
"""

import json
from fireworks.utilities.fw_serializers import FWSerializable, recursive_serialize, recursive_deserialize, \
    DATETIME_HANDLER

__author__ = 'Anubhav Jain'
__credits__ = 'Michael Kocher'
__copyright__ = 'Copyright 2012, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Dec 12, 2012'


class FWorker(FWSerializable):
    def __init__(self, name="anonymous worker", category="general worker", query=None, params=None):
        """
        :param name: the name of the resource, should be unique
        :param category: a String describing the computing resource, does not need to be unique
        :param query: a dict query that restricts the type of FireWork this resource will run
        :param params: further descriptions of this resource
        """
        self.name = name
        self.category = category
        self.query = query if query else {}
        self.params = params

    @recursive_serialize
    def to_dict(self):
        return {'name': self.name, 'category': self.category, 'query': json.dumps(self.query, default=DATETIME_HANDLER),
                'params': self.params}

    @classmethod
    @recursive_deserialize
    def from_dict(cls, m_dict):
        return FWorker(m_dict['name'], m_dict['category'], json.loads(m_dict['query']), m_dict['params'])