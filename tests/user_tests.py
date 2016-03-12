import unittest
from selenium import webdriver
from app import testing_app
from flask import current_app
from fbook.db import db
from fbook.models import User, Friend
from flask.ext.login import login_user, logout_user
import time


class StartingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = testing_app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.driver = webdriver.PhantomJS()
        self.baseURL = "http://localhost:5000/"

        self.driver.set_window_size(1124, 850)

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()       

    # --------------------------------------------------------------------------
    # User/profile tests
    # --------------------------------------------------------------------------

    # As an author, I want to befriend local authors
    def test_befriend(self):
        self.user = User(username='test_user')
        self.user.set_password('pass')
        self.user.set_id()

        self.friend = User(username='test_friend')
        self.friend.set_password('pass')
        self.friend.set_id()

        db.session.add(self.user)
        db.session.add(self.friend)
        db.session.commit()

        assert self.user in db.session
        assert self.friend in db.session
        driver.save_screenshot('test.png')

        self.driver.get(self.baseURL)
        self.driver.find_element_by_id("name").send_keys("test_user")
        self.driver.find_element_by_id("password").send_keys("pass")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(self.baseURL + "user/test_friend")
        self.driver.find_element_by_id("follow_button").click()
        self.driver.get(self.baseURL + "/logout")

        self.driver.find_element_by_id("name").send_keys("test_friend")
        self.driver.find_element_by_id("password").send_keys("pass")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(self.baseURL + "user/test_user")
        self.driver.find_element_by_id("follow_button").click()
        self.driver.get(self.baseURL + "/logout")

        test1 = Friend.query.filter_by(a_id=self.user.id, b_id=self.friend.id).first()
        test2 = Friend.query.filter_by(b_id=self.user.id, a_id=self.friend.id).first()

        assert test1 or test2

    # As an author, I want un-befriend local and remote authors
    def unfriend(self):
        test_befriend();
        driver.save_screenshot('test.png')

        self.driver.get(self.baseURL)
        self.driver.find_element_by_id("name").send_keys("test_user")
        self.driver.find_element_by_id("password").send_keys("pass")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(self.baseURL + "user/test_friend")
        self.driver.find_element_by_id("unfollow_button").click()
        self.driver.get(self.baseURL + "/logout")

        test1 = Friend.query.filter_by(a_id=self.user.id, b_id=self.friend.id).first()
        test2 = Friend.query.filter_by(b_id=self.user.id, a_id=self.friend.id).first()

        assert not test1 or not test2

    # As an author, I want to be able to use my web-browser to manage my profile
    def manage(self):
        self.user = User(username='test_user')
        self.user.set_password('pass')
        self.user.set_id()

        self.friend = User(username='test_friend')
        self.friend.set_password('pass')
        self.friend.set_id()

        db.session.add(self.user)
        db.session.add(self.friend)
        db.session.commit()

        assert self.user in db.session
        assert self.friend in db.session
        driver.save_screenshot('test.png')

        self.driver.get(self.baseURL)
        self.driver.find_element_by_id("name").send_keys("test_user")
        self.driver.find_element_by_id("password").send_keys("pass")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(self.baseURL + "settings")
        self.driver.find_element_by_id("new password").send_keys("pas")
        self.driver.find_element_by_id("new password confirm").send_keys("pas")

        assert self.user.verify_password("pas")

    # As an author, When I befriend someone it follows them, only when the other authors befriends me do I count as a real friend.
    def friend(self):
        self.user = User(username='test_user')
        self.user.set_password('pass')
        self.user.set_id()

        self.friend = User(username='test_friend')
        self.friend.set_password('pass')
        self.friend.set_id()

        db.session.add(self.user)
        db.session.add(self.friend)
        db.session.commit()

        assert self.user in db.session
        assert self.friend in db.session
        driver.save_screenshot('test.png')

        self.driver.get(self.baseURL)
        self.driver.find_element_by_id("name").send_keys("test_user")
        self.driver.find_element_by_id("password").send_keys("pass")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(self.baseURL + "user/test_friend")
        self.driver.find_element_by_id("follow_button").click()
        self.driver.get(self.baseURL + "/logout")

        test1 = Friend.query.filter_by(a_id=self.user.id, b_id=self.friend.id).first()
        test2 = Friend.query.filter_by(b_id=self.user.id, a_id=self.friend.id).first()

        assert not test1 or not test2

        test = Follow.query.filter_by(requester_id=self.user.id, requestee_id=self.friend.id).first()

        assert test

        self.driver.find_element_by_id("name").send_keys("test_friend")
        self.driver.find_element_by_id("password").send_keys("pass")
        self.driver.find_element_by_id("submit").click()

        self.driver.get(self.baseURL + "user/test_user")
        self.driver.find_element_by_id("follow_button").click()
        self.driver.get(self.baseURL + "/logout")

        test1 = Friend.query.filter_by(a_id=self.user.id, b_id=self.friend.id).first()
        test2 = Friend.query.filter_by(b_id=self.user.id, a_id=self.friend.id).first()

        assert test1 or test2




if __name__ == '__main__':
    unittest.main()
