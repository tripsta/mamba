from mamba.test import unittest
from twisted.internet import task, defer
from mamba.multirequest import service, webservice


class FullfillRequestTestCase(unittest.TestCase):

    def setUp(self):
        service.fullfill_request.set_webservice_module(webservice)

    def test_loads_registered_function_if_it_exists(self):
        request = service.BasicRequest(method='fake.ping')
        d = service.fullfill_request(request)
        d.addCallback(self.assertTrue)
        return d

    def test_raises_AttributeError_if_function_not_in_module(self):
        request = service.BasicRequest(method='fake.pong')
        self.assertRaises(AttributeError, service.fullfill_request, request)

    def test_fullfill_multirequest(self):
        request = self._make_multirequest(3)
        d = service.fullfill_request(request)
        d.addCallback(self.assertMultirequestSuccess)
        return d

    def test_list_contains_both_successes_and_failures(self):
        requests = [{"method": "fake.fail"}, {"method": "fake.ping"}]
        d = service.fullfill_request(requests)
        d.addCallback(self.assertSuccessesAndFailures, successes=1, failures=1)
        return d

    def _make_multirequest(self, how_many):
        requests = []
        for i in xrange(how_many):
            requests.append(service.BasicRequest(method='fake.ping'))

        return service.BasicMultiRequest(requests)

    def assertMultirequestSuccess(self, results):
        for status, r in results:
            self.assertTrue(status)

    def assertSuccessesAndFailures(self, results, successes, failures):
        s,f = 0,0
        for status, r in results:
            if status:
                s += 1
            else:
                f += 1

        self.assertEqual(s, successes)
        self.assertEqual(f, failures)
