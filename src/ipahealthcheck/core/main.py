#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

import logging
from os import environ
import sys

from healthcheckcore.main import run_healthcheck

logging.basicConfig(format='%(message)s')
logger = logging.getLogger()


def main():
    environ["KRB5_CLIENT_KTNAME"] = "/etc/krb5.keytab"
    environ["KRB5CCNAME"] = "MEMORY:"

    sys.exit(run_healthcheck(['ipahealthcheck.registry'],
                             '/etc/ipahealthcheck/ipahealthcheck.conf'))
