"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from sqlalchemy.orm.exc import DetachedInstanceError
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one() 
            self.assertEqual(msg.text, "Hello")

    def test_add_message_form(self):
        """Does the add message form show up?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get("/messages/new")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Testing add message form", html)

    def test_add_message_invalid_user(self):
        """Can the user look at the add message form if not logged in?"""
        with self.client as c:
            resp = c.get("/messages/new")
            resp_redirect = c.get("/messages/new", follow_redirects=True)
            html = resp_redirect.get_data(as_text=True)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp_redirect.status_code, 200)
        self.assertIn("Testing homeanon", html)

    def test_show_message(self):
        """tests that a user can view a message """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        c.post("/messages/new", data={"text": "Hello"})   
        msg = Message.query.one()
        resp = c.get(f"/messages/{msg.id}")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Testing show message", html)

    def test_destroy_message(self):
        """tests the user can delete own message and routes to correct place """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        c.post("/messages/new", data={"text": "Hello"})   
        msg = Message.query.one()
        resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
        html = resp.get_data(as_text=True)
        user = User.query.get(self.testuser.id)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Testing user profile", html)
        self.assertEqual(len(user.messages), 0)

    def test_bad_destroy_message(self):
        """tests that a user can't delete a message if logged
            or not their message """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        c.post("/messages/new", data={"text": "Hello"})   
        msg = Message.query.one()
        user = User.query.get(self.testuser.id)
        self.assertEqual(len(user.messages), 1)

        del sess[CURR_USER_KEY]

        with self.assertRaises(DetachedInstanceError):
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(len(user.messages), 1)
        self.assertEqual(resp.status_code, 200)
        

    def test_message_like(self):
        """ """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
        c.post("/messages/new", data={"text": "Hello"})
        msg = Message.query.one()
        resp = c.post(f'/messages/{msg.id}/like', data={"text": "Hello"})

        self.assertEqual(resp.status_code, 302)

    def test_bad_message_like(self):
        """Tests if user is redirected to home if not logged in 
        and attempting to like """

        with self.client as c:
            msg = Message(text="testing", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()
            resp = c.post(f'/messages/{msg.id}/like', data={"text": "Hello"}, follow_redirects=True)

        html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Testing homeanon", html)

    #TODO add test for unlike route
        
        





        
