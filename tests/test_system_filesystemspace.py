#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

from base import BaseTest
from unittest.mock import Mock
from util import capture_results
from collections import namedtuple

from healthcheckcore import config, constants
from ipahealthcheck.system.plugin import registry
from ipahealthcheck.system.filesystemspace import FileSystemSpaceCheck


class TestFileSystemNotEnoughFreeSpace(BaseTest):

    usage = namedtuple('usage', ['total', 'used', 'free'])
    usage.total = 2087428096
    usage.used = 1628193914
    usage.free = 459234182

    patches = {
        'shutil.disk_usage':
        Mock(return_value=usage),
    }

    def test_filesystem_near_enospc(self):

        framework = object()
        registry.initialize(framework)
        f = FileSystemSpaceCheck(registry)

        f.config = config.Config()
        self.results = capture_results(f)

        count = 0
        for result in self.results.results:
            if result.result == constants.ERROR:
                count += 1
                assert result.source == 'ipahealthcheck.system.filesystemspace'
                assert result.check == 'FileSystemSpaceCheck'
                assert 'free space under threshold' in result.kw.get('msg')
            else:
                assert 'free space percentage within' in result.kw.get('msg')
        assert len(self.results) == 12
        assert count == 6


class TestFileSystemNotEnoughFreeSpacePercentage(BaseTest):

    usage = namedtuple('usage', ['total', 'used', 'free'])
    usage.total = 10437140480
    usage.used = 8913305600
    usage.free = 1523834880

    patches = {
        'shutil.disk_usage':
        Mock(return_value=usage),
    }

    def test_filesystem_risking_fragmentation(self):

        framework = object()
        registry.initialize(framework)
        f = FileSystemSpaceCheck(registry)

        f.config = config.Config()
        self.results = capture_results(f)

        count = 0
        for result in self.results.results:
            if result.result == constants.ERROR:
                count += 1
                assert result.source == 'ipahealthcheck.system.filesystemspace'
                assert result.check == 'FileSystemSpaceCheck'
                assert 'free space percentage under' in result.kw.get('msg')
            else:
                assert 'free space within limits' in result.kw.get('msg')
        assert len(self.results) == 12
        assert count == 6


class TestFileSystemEnoughFreeSpace(BaseTest):

    usage = namedtuple('usage', ['total', 'used', 'free'])
    usage.total = 10437140480
    usage.used = 1523834880
    usage.free = 8913305600

    patches = {
        'shutil.disk_usage':
        Mock(return_value=usage),
    }

    def test_filesystem_with_enough_space(self):

        framework = object()
        registry.initialize(framework)
        f = FileSystemSpaceCheck(registry)

        f.config = config.Config()
        self.results = capture_results(f)

        for result in self.results.results:
            assert result.result == constants.SUCCESS
            assert result.source == 'ipahealthcheck.system.filesystemspace'
            assert result.check == 'FileSystemSpaceCheck'
            assert (
                'free space percentage within' in result.kw.get('msg') or
                'free space within limits' in result.kw.get('msg')
            )
        assert len(self.results) == 12
