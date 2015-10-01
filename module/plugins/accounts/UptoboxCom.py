# -*- coding: utf-8 -*-

import json
import re
import time

from module.plugins.internal.Account import Account


class UptoboxCom(Account):
	__name__    = "UptoboxCom"
	__type__    = "account"
	__version__ = "0.14"
	__status__  = "testing"

	__description__ = """Uptobox.com account plugin"""
	__license__     = "GPLv3"
	__authors__     = [("benbox69", "dev@tollet.me")]


	HOSTER_DOMAIN = "uptobox.com"
	HOSTER_URL    = "https://uptobox.com/"
	LOGIN_URL     = "https://login.uptobox.com/logarithme"


	def grab_info(self, user, password, data):

		return {'validuntil': '1454457600.0', 'premium': True}


	def signin(self, user, password, data):

		jsonstring = self.load(self.LOGIN_URL, None,  post={'login': user, 'password': password, 'op': 'login'})
		parsedjson = json.loads(jsonstring)
		
		if parsedjson['success'] is None:
			self.login_fail()
