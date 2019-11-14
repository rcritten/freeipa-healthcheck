#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

from healthcheckcore.plugin import Plugin, Registry


class SystemPlugin(Plugin):
    def __init__(self, registry):
        super(SystemPlugin, self).__init__(registry)
        pass


class SystemRegistry(Registry):
    def initialize(self, framework):
        pass


registry = SystemRegistry()
