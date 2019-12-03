#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

import selinux

from ipahealthcheck.system.plugin import SystemPlugin, registry
from ipahealthcheck.core.plugin import duration, Result
from ipahealthcheck.core import constants


@registry
class SELinuxContextCheck(SystemPlugin):
    """
    """

    files = {
        '/var/lib/ipa/ra-agent.pem': 'system_u:object_r:ipa_var_lib_t:s0',
    }

    @duration
    def check(self):
        for file in self.files:
            context = selinux.getfilecon(file)
            if context[1] != self.files[file]:
                yield Result(
                    self, constants.WARNING,
                    key=file,
                    got=context[1], expected=self.files[file],
                    file=file,
                    msg='Unexpected SELinux context on {file}. '
                        'Got {got}, expected {expected}.'
                )
            else:
                yield Result(self, constants.SUCCESS, key=file)
