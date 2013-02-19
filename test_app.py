import os
import app
import tempfile
import unittest

class AppTestCase(unittest.TestCase):

    def setUp(self):
        ''' setup a temp database'''
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        '''Get rid of the database again after each test.'''
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_urls(self):
        r = self.app.get('/')
        self.assertEquals(r.status_code, 200)
        r = self.app.get('/now')
        self.assertEquals(r.status_code, 200)

if __name__ == '__main__':
    unittest.main()
