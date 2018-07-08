import pytest
from flask import url_for

class HomeDash(object):

	def test_url_resolves(self, client):
		res = client.get(url_for('filter_dash'))
		assert res.status_code == 200



