#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

from healthcheckcore.plugin import Plugin, Registry


class MetaPlugin(Plugin):
    pass


class MetaRegistry(Registry):
    pass


registry = MetaRegistry()
