# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from cabot.cabotapp.tests.tests_basic import LocalTestCase
from cabot.cabotapp.models import StatusCheck, Instance
from cabot.plugins.models import StatusCheckPluginModel
from cabot_check_http.plugin import HttpStatusCheckPlugin
from cabot.cabotapp.models import Service, StatusCheckResult
from mock import Mock, patch
import os

from logging import getLogger
logger = getLogger(__name__)

def get_content(fname):
    path = os.path.join(os.path.dirname(__file__), 'fixtures/%s' % fname)
    with open(path) as f:
        return f.read()

def fake_http_200_response(*args, **kwargs):
    resp = Mock()
    resp.content = get_content('http_response.html')
    resp.status_code = 200
    return resp

def fake_http_404_response(*args, **kwargs):
    resp = Mock()
    resp.content = get_content('http_response.html')
    resp.status_code = 404
    return resp

class TestHttpStatusCheckPlugin(LocalTestCase):

    def setUp(self):
        super(TestHttpStatusCheckPlugin, self).setUp()

        self.http_check_model, created = StatusCheckPluginModel.objects.get_or_create(
	    slug='http_status'
	    )

        self.http_check = StatusCheck.objects.create(
	    check_plugin=self.http_check_model,
	    name = 'Http Check',
	    created_by=self.user,
	    importance=Service.CRITICAL_STATUS,
	    endpoint='https://arachnys.com',
	    timeout=10,
	    status_code='200',
	    text_match=None,
	    )
        self.http_check.save()
        self.http_check = StatusCheck.objects.get(pk=self.http_check.pk)
	self.service.status_checks.add(self.http_check)

    @patch('cabot.cabotapp.models.requests.get', fake_http_200_response)
    def test_run_success(self):
        http_results = self.http_check.statuscheckresult_set.all()
        self.assertEqual(len(http_results), 0)
        result = self.http_check.run()
        result.save()
        self.assertTrue(result.succeeded)
        http_results = self.http_check.statuscheckresult_set.all()
        self.assertEqual(len(http_results), 1)

    @patch('cabot.cabotapp.models.requests.get', fake_http_200_response)
    def test_test_matching(self):
	
        # Text matching
        self.http_check.text_match = u'Arachnys'
        self.http_check.save()
        self.http_check.run()
        self.assertTrue(self.http_check.last_result().succeeded)
        self.assertEqual(self.http_check.calculated_status,
                         Service.CALCULATED_PASSING_STATUS)

	# Text matching
        self.http_check.text_match = u'blah blah'
        self.http_check.save()
        self.http_check.run()
        self.assertFalse(self.http_check.last_result().succeeded)
        self.assertEqual(self.http_check.calculated_status,
                         Service.CALCULATED_FAILING_STATUS)
        # Text matching unicode
        self.http_check.text_match = u'как закалялась сталь'
        self.http_check.save()
        self.http_check.run()
        self.assertFalse(self.http_check.last_result().succeeded)
        self.assertEqual(self.http_check.calculated_status,
                         Service.CALCULATED_FAILING_STATUS)

    @patch('cabot.cabotapp.models.requests.get', fake_http_404_response)
    def test_http_run_bad_resp(self):
        http_results = self.http_check.statuscheckresult_set.all()
        self.assertEqual(len(http_results), 0)
        self.http_check.run()
        http_results = self.http_check.statuscheckresult_set.all()
        self.assertEqual(len(http_results), 1)
        self.assertFalse(self.http_check.last_result().succeeded)
        self.assertEqual(self.http_check.calculated_status,
                         Service.CALCULATED_FAILING_STATUS)

