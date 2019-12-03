#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

from base import BaseTest
from unittest.mock import Mock, patch
from util import capture_results

from ipahealthcheck.core import config, constants
from ipahealthcheck.system.plugin import registry
from ipahealthcheck.system.selinuxcontext import SELinuxContextCheck


class TestSELinuxContext(BaseTest):
    patches = {
        'selinux.is_selinux_enabled': Mock(return_value=1),
    }

    @patch('selinux.getfilecon')
    def test_context_ok(self, mock_getfilecon):
        mock_getfilecon.side_effect = [
            (0, context)
            for file, context in SELinuxContextCheck.files.items()]
        framework = object()
        registry.initialize(framework)
        f = SELinuxContextCheck(registry)

        f.config = config.Config()
        self.results = capture_results(f)

        for result in self.results.results:
            assert result.result == constants.SUCCESS
