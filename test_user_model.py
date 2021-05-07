"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
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

        self.user1 = user1
        self.user1.id = user1.id
        self.user2 = user2
        self.user2.id = user2.id

        self.client = app.test_client()

    def tearDown(self):
        """clean up any fouled transaction"""
        db.session.rollback()
        
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """tests that repr method outputs correct information """

        self.assertEqual(repr(self.user1), f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>")

    def test_is_following(self):
        """successfully detects when one user is following another user """
        user2_follows_user1 = Follows(user_being_followed_id=self.user1.id, 
                                      user_following_id=self.user2.id)
        db.session.add(user2_follows_user1)
        db.session.commit()

        self.assertFalse(self.user1.is_following(self.user2))
        self.assertTrue(self.user2.is_following(self.user1))

        # TODO check length of followers

    def test_is_followed_by(self):
        """successfully detects when one user is followed by another user """
        user2_follows_user1 = Follows(user_being_followed_id=self.user1.id, 
                                      user_following_id=self.user2.id)
        db.session.add(user2_follows_user1)
        db.session.commit()

        self.assertTrue(self.user1.is_followed_by(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))
    
    def test_User_signup(self):
        """successfully detects if a unique user can create a new account"""
        # hashed_pwd = bcrypt.generate_password_hash("HASHED_PASSWORD").decode('UTF-8')
        new_user = User.signup(username="testuser", 
                               email="test@test.com", 
                               password="HASHED_PASSWORD",
                               image_url="")
        db.session.commit()

        fail_new_user = User.signup(username="testuser", 
                               email="test@test.com", 
                               password="HASHED_PASSWORD",
                               image_url="")

        with self.assertRaises(IntegrityError):
            db.session.commit()
        self.assertIsInstance(new_user, User)

    def test_User_authenticate(self):
        """successfully detects if an exisiting user can log into Warbler"""

        new_user = User.signup(username="testuser", 
                               email="test@test.com", 
                               password="HASHED_PASSWORD",
                               image_url="")
        db.session.commit()

        with self.assertRaises(ValueError):
            User.authenticate(username="testuser1",
                              password="BAD_TEST_PASSWORD")

        self.assertFalse(User.authenticate(username="baduser",
                                           password="TEST_PASSWORD"))
 
        self.assertTrue(User.authenticate(username="testuser",
                                          password="HASHED_PASSWORD"))





     





    
       


