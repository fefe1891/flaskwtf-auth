import unittest
from app import app
from models import db, User

class FlaskTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        "This method is run once for each Test Class before any tests are run"

    @classmethod
    def tearDownClass(cls):
        "This method is run once for each Test Class _after_ all tests are run"

    def setUp(self):
        "This method is run once before _each_ test method is executed"
        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        "This method is run once after _each_ test method is executed"

    def test_home_page_redirect(self):
        "Test if the home page redirects correctly"
        response = self.client.get('/', follow_redirects=True)
        self.assertIn(b'Register', response.data) 
        # b'Register' because response.data returns a byte string, 'Register' is expected to appear in the HTML of registration page

    def test_register_page(self):
        "Test if registration page is displayed and form is present"
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username', response.data)
        self.assertIn(b'Password', response.data)

if __name__ == "__main__":
    unittest.main()