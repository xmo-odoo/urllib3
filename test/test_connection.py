import datetime
import sys
if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest

import mock

from urllib3.connection import (
    CertificateError,
    _match_hostname,
    RECENT_DATE
)


class TestConnection(unittest.TestCase):
    """
    Tests in this suite should not make any network requests or connections.
    """
    def test_match_hostname_no_cert(self):
        cert = None
        asserted_hostname = 'foo'
        self.assertRaises(ValueError, _match_hostname, cert, asserted_hostname)

    def test_match_hostname_empty_cert(self):
        cert = {}
        asserted_hostname = 'foo'
        self.assertRaises(ValueError, _match_hostname, cert, asserted_hostname)

    def test_match_hostname_match(self):
        cert = {'subjectAltName': [('DNS', 'foo')]}
        asserted_hostname = 'foo'
        _match_hostname(cert, asserted_hostname)

    def test_match_hostname_mismatch(self):
        cert = {'subjectAltName': [('DNS', 'foo')]}
        asserted_hostname = 'bar'
        try:
            with mock.patch('urllib3.connection.log.error') as mock_log:
                _match_hostname(cert, asserted_hostname)
        except CertificateError as e:
            self.assertEqual(str(e), "hostname 'bar' doesn't match 'foo'")
            mock_log.assert_called_once_with(
                'Certificate did not match expected hostname: %s. '
                'Certificate: %s',
                'bar', {'subjectAltName': [('DNS', 'foo')]}
            )
            self.assertEqual(e._peer_cert, cert)

    def test_recent_date(self):
        # This test is to make sure that the RECENT_DATE value
        # doesn't get too far behind what the current date is.
        # When this test fails update urllib3.connection.RECENT_DATE
        # according to the rules defined in that file.
        two_years = datetime.timedelta(days=365 * 2)
        self.assertGreater(RECENT_DATE, (datetime.datetime.today() - two_years).date())


if __name__ == '__main__':
    unittest.main()
