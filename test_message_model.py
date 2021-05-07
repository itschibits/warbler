# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User(
            email="testemail@test.com",
            username="testuser1",
            password="TEST_PASSWORD"
        )
        user2 = User(
            email="testemail2@test.com",
            username="testuser2",
            password="TEST_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        message1 = Message(text="test", user_id=user1.id)
        db.session.add(message1)
        db.session.commit()

        self.user1 = user1
        self.user1.id = user1.id
        self.user2 = user2
        self.user2.id = user2.id
        self.message1 = message1
        self.message1.id = message1.id

        self.client = app.test_client()

    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()
        
    def test_message_model(self):
        """Does basic model work?"""

        message = Message(text="test2", user_id=self.user2.id)

        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.user2.messages), 1)
        self.assertIsInstance(message, Message)
        self.assertEqual(message.text, "test2")

    def test_like_message(self):
        test_like = Like(user_id=self.user1.id, message_id=self.message1.id)
        db.session.add(test_like)
        db.session.commit()

        self.assertIsInstance(test_like, Like)
        self.assertEqual(len(self.user1.likes), 1)

    def test_unlike_message(self):
        test_like = Like(user_id=self.user1.id, message_id=self.message1.id)
        db.session.add(test_like)
        db.session.commit()

        self.assertEqual(len(self.user1.likes), 1)

        db.session.delete(test_like)
        db.session.commit()

        self.assertEqual(len(self.user1.likes), 0)
