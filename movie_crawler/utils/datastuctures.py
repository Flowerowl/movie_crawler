# encoding: utf-8
from __future__ import unicode_literals

from UserDict import UserDict  # can't use super, fu*k old style class


class DictIgnoreSpace(UserDict):

    def update(self, dict=None, **kwargs):
        if dict:
            for k, v in dict.items():
                self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def _remove_space(self, key):
        return ''.join(key.split())

    def __setitem__(self, key, item):
        key = self._remove_space(key)
        return UserDict.__setitem__(self, key, item)

    def __getitem__(self, key):
        key = self._remove_space(key)
        return UserDict.__getitem__(self, key)

    def __delitem__(self, key):
        key = self._remove_space(key)
        return UserDict.__delitem__(self, key)

    def __contains__(self, key):
        key = self._remove_space(key)
        return UserDict.__contains__(self, key)
