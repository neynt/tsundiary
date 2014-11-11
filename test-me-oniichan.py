import tsundiary
import os
import tempfile
import unittest

class TsundiaryTestCase(unittest.TestCase):
    def setUp(self):
        tsundiary.models.init_db()
        self.app = tsundiary.app.test_client()

    def tearDown(self):
        pass

    def register(self, username, password, email=""):
        return self.app.post('/register', data=dict(
            username=username,
            password=password,
            password_confirm=password,
            email=email,
            invite_key="haha yolo"
        ), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/attempt_login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self, username):
        return self.app.get('/logout?user=%s' % username, follow_redirects=True)

    def test_empty_db(self):
        rv = self.app.get('/secret_userlist')
        assert 'secret userlist' in rv.data

    def test_register_login(self):
        rv = self.register("testuser123", "12345pineapple")
        self.logout("testuser123")
        rv = self.login("testuser123", "fake")
        assert 'don&#39;t recognize you, sorry.' in rv.data
        rv = self.login("testuser123", "12345pineapple")
        assert 'Once you have a history' in rv.data

    def test_settings(self):
        rv = self.register("testuser123", "12345pineapple")
        rv = self.login("testuser123", "12345pineapple")
        assert 'Once you have a history' in rv.data
        rv = self.app.get('/settings')
        assert 'Change password' in rv.data
        rv = self.app.post('/change_setting', data={
            'setting_name': 'theme',
            'setting_value': 'saya'
            })
        assert 'refresh to see theme' in rv.data
        rv = self.app.get('/settings')
        assert 'Saya source' in rv.data

if __name__ == '__main__':
    print("Onii-chan, your test suite is too comprehensive!!")
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(TsundiaryTestCase)
    )
