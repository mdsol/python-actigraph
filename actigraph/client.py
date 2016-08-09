# -*- coding: UTF-8 -*-
__author__ = 'isparks'

import requests
import datetime
import hmac
import hashlib
import base64
from six.moves.urllib.parse import urlencode

SECONDS_IN_24_HOURS = 24 * 60 * 60

def isodatetime(dt):
    """Takes a date, returns ISO8601 date/time format"""
    return dt.strftime('%Y-%m-%dT%H:%M:%S')

def isodate(dt):
    """Takes a date, returns ISO8601 date format"""
    return dt.strftime('%Y-%m-%d')

class ActigraphAuth(requests.auth.AuthBase):
    """Custom requests authorizer for Actigraph"""
    def __init__(self, base_url, access_key, secret_key):
        self.base_url = base_url
        self.access_key = access_key.encode('utf-8')
        self.secret_key = secret_key.encode('utf-8')

    def __call__(self, r):
        """Call is made like:
           requests.get(url, auth=MyAuth())
        """
        r.headers.update(self.make_headers(r.url))
        return r

    def sign(self, signature_string):
        """Return the signed value of the signature string"""
        return base64.b64encode(hmac.new(self.secret_key,
                                         signature_string.encode('utf-8'),
                                         hashlib.sha256).digest())

    def make_url(self, resource_url):
        """
        Return full URL
        """
        url = u"%s%s" % (self.base_url, resource_url,)
        return url

    def make_headers(self, url):
        """Make headers for the request."""

        #Get the time of the request
        date_time = datetime.datetime.utcnow()

        #Make signature string
        signature_string = self.make_signature_string(url, date_time)

        #Sign it
        signed = self.sign(signature_string)

        #Set the headers
        headers = self.make_authentication_headers(signed, date_time)

        return headers

    def make_authentication_headers(self, signed_string, dt):
        """Makes headers for Authorization and date, including the access key and the string signed with
           the secret key

           Date must be in form '%a, %d %b %Y %H:%M:%S +0000' eg. Tue, 27 Mar 2007 19:36:42 +0000 or Actigraph will
           fail the request.

        """
        return {
                'Authorization' : u"AGS {}:{}".format(self.access_key.decode('utf-8'),
                                                      signed_string.decode('utf-8')),
                'Date' : dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
                }

    def make_signature_string(self, url_path, dt):
        """Makes a signature string for signing of the form:

            https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/authentication.md

            StringToSign = HTTP-Verb + "\n" +
                Content-MD5 + "\n" +
                Content-Type + "\n" +
                Date + "\n" +
                CanonicalizedResource;

            CanonicalizedResource = <HTTP-Request-URI, from the protocol name up to the query string>;

            (Canonicalization doesn't mean anything, URI is passed as-is including query string, quirk of Actigraph docs)

            Date must be in ISO form.

            Returns the encoded string

        """
        #API only has GET requests so there is no body to md5 hash, verb is always GET and content type is always ''
        vals = dict(body_md5 = '',
                    verb='GET',
                    url_path=url_path,
                    date=isodatetime(dt),
                    content_type='',
                    )

        string_to_sign = '{verb}\n{body_md5}\n{content_type}\n{date}Z\n{url_path}'.format(**vals)
        return string_to_sign


class ActigraphClient(object):
    """A simple client that wraps the requests and authorization"""
    def __init__(self, base_url, access_key, secret_key):
        self.auth = ActigraphAuth(base_url, access_key, secret_key)

    def get(self, api_url):
        """Make a get request"""
        url = self.auth.make_url(api_url)
        #Verify = False because actigraph SSL cert signed by authority that is not in requests root cert store
        #TODO: Check that Verify still required
        return requests.get(url, auth=self.auth, verify=False)

    def _check_start_end(self, start, end):
        """Check start < end or raise ValueError"""
        if not start < end:
            raise ValueError("Start time after End Time")

    def _check_twenty_four_hours(self, start, end):
        """If difference between start and end > 24Hours raise ValueError"""
        # Cannot be greater than 24 hour gap
        diff = end - start
        if diff.total_seconds() > SECONDS_IN_24_HOURS:
            raise ValueError("Date span is greater than 24 hours")

    #- API Methods -----------------------------------------------------------------------------------------------------

    def get_all_studies(self):
        """
        Get all studies that these credentials can access

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/studies.md#get-all-studies
        """
        url = "/v1/studies"
        return self.get(url)

    def get_study(self, study_id):
        """
        Get details of a particular study

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/studies.md#get-a-study
        """
        url = "/v1/studies/{0!s}".format(study_id)
        return self.get(url)

    def get_all_subjects(self, study_id):
        """
        Get all subjects for a study

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/studies.md#get-all-subjects-within-a-study
        """
        url = "/v1/studies/{0!s}/subjects".format(study_id)
        return self.get(url)

    def get_subject(self, subject_id):
        """
        Get Subject Details

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-a-subject
        """
        url = "/v1/subjects/{0!s}".format(subject_id)
        return self.get(url)


    def get_subject_stats(self, subject_id):
        """
        Get Subject Statistics

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-overall-stats-for-a-subject
        """
        url = "/v1/subjects/{0!s}/stats".format(subject_id)
        return self.get(url)

    def get_subject_daily_stats(self, subject_id):
        """
        Get Daily stats for a subject

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-daily-stats-for-a-subject
        """
        url = "/v1/subjects/{0!s}/daystats".format(subject_id)
        return self.get(url)

    def get_subject_daily_minutes(self, subject_id, date):
        """
        Get daily minutes for subject

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-daily-minutes-for-a-subject
        """
        url = "/v1/subjects/{0!s}/dayminutes/{1}".format(subject_id, isodate(date))
        return self.get(url)

    def get_subject_sleep_epochs(self, subject_id, inbed, outbed):
        """
        Get Sleep Epochs for a subject
        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-sleep-epochs-for-a-subject-v11
        """
        # Validations
        self._check_start_end(inbed, outbed)
        self._check_twenty_four_hours(inbed, outbed)

        url = "/v1/subjects/{0!s}/sleepepochs?inbed={1}&outbed={2}".format(subject_id, isodatetime(inbed), isodatetime(outbed))
        return self.get(url)

    def get_subject_sleep_score(self, subject_id, inbed, outbed):
        """
        Get Sleep Score for a subject

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-sleep-score-for-a-subject-v11
        """

        # Validations
        self._check_start_end(inbed, outbed)
        self._check_twenty_four_hours(inbed, outbed)

        url = "/v1/subjects/{0!s}/sleepscore?inbed={1}&outbed={2}".format(subject_id, isodatetime(inbed), isodatetime(outbed))
        return self.get(url)

    def _mergeStartStopParams(self, url, start, stop):
        """Merge optional Start and Stop params into a URL string"""
        params = {}
        if start:
            params['start'] = isodatetime(start)
        if stop:
            params['stop'] = isodatetime(stop)

        if params:
            #Actigraph API does not like urlencoded : characters
            url = "{0}?{1}".format(url, urlencode(params)).replace('%3A',':')
        return url

    def get_subject_bout_periods(self, subject_id, start=None, stop=None):
        """
        Get Subject Bout periods (when they are wearing and not wearing device)

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-bout-periods-for-a-subject-v12
        """
        url = "/v1/subjects/{0!s}/bouts".format(subject_id)

        if start and stop:
            self._check_start_end(start, stop)

        url = self._mergeStartStopParams(url, start, stop)

        return self.get(url)

    def get_subject_bed_times(self, subject_id, start=None, stop=None):
        """
        Get Subject in and out of bed times

        https://github.com/actigraph/StudyAdminAPIDocumentation/blob/master/sections/subjects.md#get-bed-times-for-a-subject-v13
        """
        url = "/v1/subjects/{0!s}/bedtimes".format(subject_id)

        if start and stop:
            self._check_start_end(start, stop)

        url = self._mergeStartStopParams(url, start, stop)

        return self.get(url)
