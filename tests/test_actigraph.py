__author__ = 'isparks'

import unittest
import datetime
import requests
import mock
from six.moves.urllib.parse import urlparse, parse_qs

from actigraph.client import ActigraphAuth, ActigraphClient, isodate, isodatetime


EXAMPLE_ACCESS_KEY = u'testaccesskey'
EXAMPLE_SECRET_KEY = u'testsecretkey'


def assert_urls_equal(a, b):
    # Asserts two URLS match, working around the vagueries of query string ordering
    _a = urlparse(a)
    _b = urlparse(b)
    if _a.path == _b.path:
        if parse_qs(_a.query) == parse_qs(_b.query):
            return True
    return False

class TestUtils(unittest.TestCase):
    """Test utility functions"""
    def test_date_formatting(self):
        dt = datetime.datetime(2014, 1, 9)
        self.assertEqual('2014-01-09', isodate(dt))


class TestRawAuthorizer(unittest.TestCase):
    """Test of making a call just with the authorizer and raw requests"""

    def test_raw_auth(self):
        auth = ActigraphAuth('http://example.com', EXAMPLE_SECRET_KEY, EXAMPLE_ACCESS_KEY)

        #Mock request
        class MockRequest(object):
            def __init__(self, url):
                self.headers = {}
                self.url = url

        result = auth(MockRequest('http://example.com/v1/studies'))

        self.assertTrue(True, 'Authorization' in result.headers)
        self.assertTrue(True, 'Date' in result.headers)

class TestAuthClient(unittest.TestCase):
    """Test auth client functions"""
    def setUp(self):
        self.ac = ActigraphAuth('http://example.com',EXAMPLE_ACCESS_KEY,EXAMPLE_SECRET_KEY)

    def test_make_signature_string(self):
        """Test formatting of signature string"""
        dt = datetime.datetime.strptime('2007-03-27T19:36:42','%Y-%m-%dT%H:%M:%S')
        tested = self.ac.make_signature_string('https://studyadmin-api.actigraphcorp.com/v1/studies',dt)
        self.assertEqual("GET\n\n\n2007-03-27T19:36:42Z\nhttps://studyadmin-api.actigraphcorp.com/v1/studies", tested)

    def test_signature(self):
        """Test signature against example from Actigraph website"""
        #https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/authentication.md#example-1
        tested = self.ac.sign("GET\n\n\n2014-06-19T15:14:31Z\nhttps://studyadmin-api.actigraphcorp.com/v1/studies")
        self.assertEqual("J+9FTQTAkfGmUsaRmB/HBMJOXG+4Xqbo3drXBVQwZ4o=", tested.decode('utf-8'))

    def test_make_headers(self):
        """Test formatting of headersg"""
        dt = datetime.datetime.strptime('2007-03-27T19:36:42','%Y-%m-%dT%H:%M:%S')

        headers = self.ac.make_authentication_headers('TEST_SIGNED_STRING'.encode('utf-8'), dt)

        self.assertEqual('Tue, 27 Mar 2007 19:36:42 +0000',headers['Date'])
        self.assertEqual(u'AGS %s:TEST_SIGNED_STRING' % self.ac.access_key.decode('utf-8'), headers['Authorization'])


    def test_make(self):
        """Test the _make method"""

        fixed_time = datetime.datetime(2014, 1, 1, 15, 33)

        #Patching datetime utcnow to return a fixed date so signature can be verified since date-based
        @mock.patch('datetime.datetime')
        def test_date(mock_dt):
            mock_dt.utcnow.return_value = fixed_time

            headers = self.ac.make_headers(self.ac.make_url("/v1/studies"))

            self.assertEqual(u'AGS testaccesskey:HiPTGTljix5BP+cTLwCGLA23pYL2E1jFDLzrVjuxUJE=',
                             headers['Authorization'])

        #Run it
        test_date()


class ACMockTests(unittest.TestCase):
    """
    Base class for tests that exercise the ActigraphClient class
    """
    def setUp(self):
        self.ac = ActigraphClient('http://example.com',EXAMPLE_ACCESS_KEY,EXAMPLE_SECRET_KEY)

class TestClientValidations(ACMockTests):
    """
    Tests that exercise the validations on parameters to functions
    """
    def test_sleep_score_gt_24_hours(self):
        """Cannot request a > 24 hour span"""

        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)

        def do():
            self.ac.get_subject_sleep_score(999, inbed, inbed + datetime.timedelta(hours=24, seconds=1) )

        self.assertRaises(ValueError, do)

    def test_sleep_score_start_after_end(self):
        """Start must be before end"""
        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)
        def do():
            self.ac.get_subject_sleep_score(999, inbed, inbed + datetime.timedelta(seconds=-1) )
        self.assertRaises(ValueError, do)

    def test_sleep_epochs_gt_24_hours(self):
        """Cannot request a > 24 hour span"""

        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)

        def do():
            self.ac.get_subject_sleep_epochs(999, inbed, inbed + datetime.timedelta(hours=24, seconds=1) )

        self.assertRaises(ValueError, do)

    def test_sleep_epochs_start_after_end(self):
        """Start must be before end"""
        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)
        def do():
            self.ac.get_subject_sleep_epochs(999, inbed, inbed + datetime.timedelta(seconds=-1) )
        self.assertRaises(ValueError, do)

    def test_subject_bouts_start_after_end(self):
        """Start must be before end"""
        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)
        def do():
            self.ac.get_subject_bout_periods(999, inbed, inbed + datetime.timedelta(seconds=-1) )
        self.assertRaises(ValueError, do)

class TestClientURLs(ACMockTests):
    """Gratuituous tests of URL building to get test coverage"""

    def test_get_all_studies(self):
        self.ac.get = mock.MagicMock('get')
        self.ac.get_all_studies()
        self.ac.get.assert_called_once_with('/v1/studies')

    def test_get_study(self):
        self.ac.get = mock.MagicMock('get')
        self.ac.get_study(123)
        self.ac.get.assert_called_once_with('/v1/studies/123')

    def test_get_all_subjects(self):
        self.ac.get = mock.MagicMock('get')
        self.ac.get_all_subjects(9)
        self.ac.get.assert_called_once_with('/v1/studies/9/subjects')

    def test_get_subject(self):
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject(123)
        self.ac.get.assert_called_once_with('/v1/subjects/123')

    def test_get_subject_stats(self):
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_stats(123)
        self.ac.get.assert_called_once_with('/v1/subjects/123/stats')

    def test_get_subject_daily_stats(self):
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_daily_stats(123)
        self.ac.get.assert_called_once_with('/v1/subjects/123/daystats')

    def test_getSubjectDailyMinutes(self):
        self.ac.get = mock.MagicMock('get')
        dt = datetime.datetime(2014, 6, 11)
        self.ac.get_subject_daily_minutes(123, dt)
        self.ac.get.assert_called_once_with('/v1/subjects/123/dayminutes/%s' % isodate(dt))

    def test_subject_bouts_simple(self):
        """Check format of url with no parameters passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bout_periods(999)
        self.ac.get.assert_called_once_with('/v1/subjects/999/bouts')

    def test_subject_bouts_start_only(self):
        """Check format of url with start parameter passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bout_periods(999,start=datetime.datetime(2014, 5, 29, 20, 0, 0))
        self.ac.get.assert_called_once_with('/v1/subjects/999/bouts?start=2014-05-29T20:00:00')

    def test_subject_bouts_stop_only(self):
        """Check format of url with end parameter passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bout_periods(999,stop=datetime.datetime(2014, 5, 30, 20, 0, 0))
        self.ac.get.assert_called_once_with('/v1/subjects/999/bouts?stop=2014-05-30T20:00:00')

    def test_subject_bouts_both(self):
        """Check format of url with start and end parameter passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bout_periods(999,start=datetime.datetime(2014, 5, 29, 20, 0, 0),stop=datetime.datetime(2014, 5, 30, 20, 0, 0))
        # this is slightly more difficult given how the ordering of the params can change
        self.assertEqual(1, self.ac.get.call_count)
        self.assertTrue(assert_urls_equal('/v1/subjects/999/bouts?start=2014-05-29T20:00:00&stop=2014-05-30T20:00:00',
                                          self.ac.get.call_args[0][0]))

    def test_subject_bed_times_simple(self):
        """Check format of url with no parameters passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bed_times(999)
        self.ac.get.assert_called_once_with('/v1/subjects/999/bedtimes')

    def test_subject_bed_times_start_only(self):
        """Check format of url with start parameter passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bed_times(999,start=datetime.datetime(2014, 5, 29, 20, 0, 0))
        self.ac.get.assert_called_once_with('/v1/subjects/999/bedtimes?start=2014-05-29T20:00:00')

    def test_subject_bed_times_stop_only(self):
        """Check format of url with end parameter passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bed_times(999,stop=datetime.datetime(2014, 5, 30, 20, 0, 0))
        self.ac.get.assert_called_once_with('/v1/subjects/999/bedtimes?stop=2014-05-30T20:00:00')

    def test_subject_bed_times_both(self):
        """Check format of url with start and end parameter passed"""
        self.ac.get = mock.MagicMock('get')
        self.ac.get_subject_bed_times(999,
                                      start=datetime.datetime(2014, 5, 29, 20, 0, 0),
                                      stop=datetime.datetime(2014, 5, 30, 20, 0, 0))
        # this is slightly more difficult given how the ordering of the params can change
        self.assertEqual(1, self.ac.get.call_count)
        self.assertTrue(
            assert_urls_equal('/v1/subjects/999/bedtimes?start=2014-05-29T20:00:00&stop=2014-05-30T20:00:00',
                              self.ac.get.call_args[0][0]))

    def test_subject_sleep_score(self):
        """Check format of url"""
        self.ac.get = mock.MagicMock('get')
        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)
        outbed = datetime.datetime(2014, 5, 30, 20, 0, 0)
        self.ac.get_subject_sleep_score(999,inbed, outbed)
        # this is slightly more difficult given how the ordering of the params can change
        self.assertEqual(1, self.ac.get.call_count)
        self.assertTrue(
            assert_urls_equal('/v1/subjects/999/sleepscore?inbed=%s&outbed=%s' % (isodatetime(inbed),
                                                                                  isodatetime(outbed)),
                              self.ac.get.call_args[0][0]))

    def test_subject_sleep_epochs(self):
        """Check format of url with start and end parameter passed"""
        self.ac.get = mock.MagicMock('get')
        inbed = datetime.datetime(2014, 5, 29, 20, 0, 0)
        outbed = datetime.datetime(2014, 5, 30, 20, 0, 0)
        self.ac.get_subject_sleep_epochs(999,inbed, outbed)
        # this is slightly more difficult given how the ordering of the params can change
        self.assertEqual(1, self.ac.get.call_count)
        self.assertTrue(
            assert_urls_equal('/v1/subjects/999/sleepepochs?inbed=%s&outbed=%s' % (isodatetime(inbed),
                                                                                   isodatetime(outbed)),
                              self.ac.get.call_args[0][0]))


class TestPatchRequests(ACMockTests):
    """Gratuituous test patching requests.get to get to 100% coverage"""

    def test_getAllStudies(self):
        with mock.patch('actigraph.client.requests.get') as mocked:
            self.ac.get_all_studies()
            # Mocked call url we made is the first mocked call, second parameter, first element
            self.assertEqual('http://example.com/v1/studies',mocked.mock_calls[0][1][0])


if __name__ == '__main__':
    unittest.main()
