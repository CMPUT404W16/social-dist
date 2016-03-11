import unittest
from selenium import webdriver

class StartingTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.baseURL = "http://localhost:5000/"
        self.driver.set_window_size(1120, 550)

    def tearDown(self):
        self.driver.quit()

    # --------------------------------------------------------------------------
    # User/profile tests
    # --------------------------------------------------------------------------

    # As an author, I want to befriend local authors
    def test_home(self):
        self.driver.get(self.baseURL)
        assert "fbook" == self.driver.title

    def test_home_envio_form(self):
        self.driver.get(self.baseURL)
        self.driver.find_element_by_id("texto").send_keys("Resuma isso!")
        self.driver.find_element_by_id("btnSubmit").click()
        resumo = self.driver.find_element_by_id("txt_resumo").text
        assert "Resuma isso!" in resumo

    def test_sample_text(self):
        self.driver.get(self.baseURL)
        self.driver.find_element_by_link_text("Sample 1").click()
        self.driver.find_element_by_id("btnSubmit").click()
        self.assertIn("hello.",
                self.driver.find_element_by_id("txt_resumo").text)

if __name__ == '__main__':
    unittest.main()
