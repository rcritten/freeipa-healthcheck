#
# Copyright (C) 2019 FreeIPA Contributors see COPYING for license
#

import logging

from ipahealthcheck.dogtag.plugin import DogtagPlugin, registry
from ipahealthcheck.core.plugin import Result
from ipahealthcheck.core.plugin import duration
from ipahealthcheck.core import constants

from ipalib import api
from ipaplatform.paths import paths
from ipaserver.install import certs
from ipaserver.install import krainstance
from ipapython.directivesetter import get_directive
from cryptography.hazmat.primitives.serialization import Encoding

logger = logging.getLogger()


@registry
class DogtagCertsConfigCheck(DogtagPlugin):
    """
    Compare the cert blob in the NSS database to that stored in CS.cfg
    """
    @duration
    def check(self):
        if not self.ca.is_configured():
            logger.debug("No CA configured, skipping dogtag config check")
            return

        kra = krainstance.KRAInstance(api.env.realm)

        blobs = {'auditSigningCert cert-pki-ca': 'ca.audit_signing.cert',
                 'ocspSigningCert cert-pki-ca': 'ca.ocsp_signing.cert',
                 'caSigningCert cert-pki-ca': 'ca.signing.cert',
                 'subsystemCert cert-pki-ca': 'ca.subsystem.cert',
                 'Server-Cert cert-pki-ca': 'ca.sslserver.cert'}

        # Nicknames to skip because their certs are not in CS.cfg
        skip = []

        if kra.is_installed:
            kra_blobs = {
                'transportCert cert-pki-kra':
                'ca.connector.KRA.transportCert',
            }
            blobs.update(kra_blobs)
            skip.append('storageCert cert-pki-kra')
            skip.append('auditSigningCert cert-pki-kra')

        db = certs.CertDB(api.env.realm, paths.PKI_TOMCAT_ALIAS_DIR)
        for nickname, _trust_flags in db.list_certs():
            if nickname in skip:
                logging.debug('Skipping nickname %s because it isn\'t in '
                              'the configuration file')
                continue
            try:
                val = get_directive(paths.CA_CS_CFG_PATH,
                                    blobs[nickname], '=')
            except KeyError:
                print("%s not found, assuming 3rd party" % nickname)
                continue
            if val is None:
                yield Result(self, constants.ERROR,
                             key=nickname,
                             configfile=paths.CA_CS_CFG_PATH,
                             msg='Certificate %s not found in %s' %
                             (blobs[nickname], paths.CA_CS_CFG_PATH))
                continue
            cert = db.get_cert_from_db(nickname)
            pem = cert.public_bytes(Encoding.PEM).decode()
            pem = pem.replace('\n', '')
            pem = pem.replace('-----BEGIN CERTIFICATE-----', '')
            pem = pem.replace('-----END CERTIFICATE-----', '')

            if pem.strip() != val:
                yield Result(self, constants.ERROR,
                             key=nickname,
                             directive=blobs[nickname],
                             configfile=paths.CA_CS_CFG_PATH,
                             msg='Certificate %s does not match the value '
                             'of %s in  %s' %
                             (nickname, blobs[nickname], paths.CA_CS_CFG_PATH))
            else:
                yield Result(self, constants.SUCCESS,
                             key=nickname,
                             configfile=paths.CA_CS_CFG_PATH)
