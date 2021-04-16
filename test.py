import unittest
import netlas
from dotenv import dotenv_values

config = dotenv_values(".env")


class NetlasTests(unittest.TestCase):
    DATATYPES = ['response', 'cert', 'domain']

    RESPONSE_QUERIES = {'small': 'port:7001', 'empty': 'UIDY&Sdyh&*dhkjkljhas'}

    CERT_QUERIES = {
        'small': 'certificate.subject.country:US',
        'empty': 'UIDY&Sdyh&*dhkjkljhas'
    }

    DOMAIN_QUERIES = {
        'small': 'mx:mail.google.com',
        'empty': 'UIDY&Sdyh&*dhkjkljhas'
    }

    def setUp(self):
        self.netlas = netlas.Netlas(api_key=config['TEST_API_KEY'],
                                    apibase=config['TEST_API_SERVER'],
                                    debug=True)

    def test_response_query(self):
        results = self.netlas.query(query=self.RESPONSE_QUERIES['empty'],
                                    datatype="response")
        self.assertIn('items', results)
        self.assertCountEqual([], results['items'])

        results = self.netlas.query(query=self.RESPONSE_QUERIES['small'],
                                    datatype="response")
        self.assertIn('items', results)
        self.assertIn('data', results['items'][0])

    def test_cert_query(self):
        results = self.netlas.query(query=self.CERT_QUERIES['empty'],
                                    datatype="cert")
        self.assertIn('items', results)
        self.assertCountEqual([], results['items'])

        results = self.netlas.query(query=self.CERT_QUERIES['small'],
                                    datatype="cert")
        self.assertIn('items', results)
        self.assertIn('data', results['items'][0])

    def test_domain_query(self):
        results = self.netlas.query(query=self.DOMAIN_QUERIES['empty'],
                                    datatype="domain")
        self.assertIn('items', results)
        self.assertCountEqual([], results['items'])

        results = self.netlas.query(query=self.DOMAIN_QUERIES['small'],
                                    datatype="domain")
        self.assertIn('items', results)
        self.assertIn('data', results['items'][0])

    def test_response_download(self):
        bin_results: bytes = b''
        for results in self.netlas.download(
                query=self.RESPONSE_QUERIES['small'],
                datatype="response",
                size=1,
        ):
            bin_results += results
        self.assertLess(b'', bin_results)

    def test_cert_download(self):
        bin_results: bytes = b''
        for results in self.netlas.download(
                query=self.CERT_QUERIES['small'],
                datatype="cert",
                size=1,
        ):
            bin_results += results
        self.assertLess(b'', bin_results)

    def test_domain_download(self):
        bin_results: bytes = b''
        for results in self.netlas.download(
                query=self.DOMAIN_QUERIES['small'],
                datatype="domain",
                size=1,
        ):
            bin_results += results
        self.assertLess(b'', bin_results)

    def test_profile(self):
        results = self.netlas.profile()
        self.assertIn('email', results)


if __name__ == '__main__':
    unittest.main()
