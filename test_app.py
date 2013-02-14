import os
import app
import tempfile
import unittest

class AppTestCase(unittest.TestCase):

    def setup(self):
        ''' setup a temp database'''
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.app.test_client()
        app.app.connect_db()

    def tearDown(self):
        '''Get rid of the database again after each test.'''
        try:
            os.close(self.db_fd)
            os.unlink(app.app.config['DATABASE'])
        except:
            pass

    def test_urls(self):
        r = self.app.get('/')
        self.assertEquals(r.status_code, 200)

if __name__ == '__main__':
    unittest.main()
