import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains

import os
from dotenv import load_dotenv

load_dotenv()


class Scraper:

    def __init__(self):
        self.driver = None
        self.base_url = 'https://asu.mathgpt.ai/'

    def init_browser(self):
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-save-password-bubble")


        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        #options.add_argument('--headless')
        self.driver = uc.Chrome(options=options)
    
    def scrape(self):
        url = 'https://asu.mathgpt.ai/'
        self.driver.get(url)
        html = self.driver.page_source
        print(html)

            
    def log_in(self):
        self.driver.get(self.base_url)
        # XPath to find a button or link with the exact text "Log in as a Student"
        log_in_xpath = "//button[.//div[contains(text(), 'Log In')]] | //a[.//div[contains(text(), 'Log In')]]"
        log_in_student_xpath = "//button[contains(text(), 'Log in as a Student')] | //a[contains(text(), 'Log in as a Student')]"
        # Wait up to 10 seconds for the button to be present
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, log_in_xpath))
        )
        login_button.click()

        student_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, log_in_student_xpath))
        )
        student_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'email'))
        ).send_keys(os.getenv('MATHGPT_USER'), Keys.ENTER)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, 'password'))
        ).send_keys(os.getenv('MATHGPT_PASSWORD'), Keys.ENTER)

    def click_on_course(self, selected_course_name):
        wait = WebDriverWait(self.driver, 10)  # Adjust the timeout as needed
        course_items = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//*[contains(@class, 'CourseItemContentWrapper')]")))
        #course_items = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'CourseItemContentWrapper')]")


        for item in course_items:

            course_name = item.find_element(By.XPATH, ".//div[1]").get_attribute('innerHTML')
            print(f'Found course {course_name}')

            if course_name == selected_course_name:
                try:
                    get_started_button = item.find_element(By.XPATH, "./following-sibling::div//button[.//span[text()='Get started']]")
                    get_started_button.click()
                    break
                except Exception as e:
                    print(f"Error finding or clicking 'Get Started' button: {e}")

    def click_on_sidebar_submenu(self, span_str):

        xpath = f"//*[contains(@class, 'SidebarSubItemWrapper')]//span//div//span[contains(text(), '{span_str}')]/ancestor::*[contains(@class, 'SidebarSubItemWrapper')][1]"
        content_menu_item = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        #print(content_menu_item.get_attribute('outerHTML'))
        #self.driver.execute_script("arguments[0].style.border='3px solid red'", content_menu_item)

        content_menu_item.click()

    def expand_sidebar(self):

        clicked = set()
        xpath_pattern = "//*[contains(@class, 'SidebarMenu-subMenu')]//div//span//div//span/ancestor::*[contains(@class, 'SidebarMenu-subMenu')]"

        while True:
            found = False
            wait = WebDriverWait(self.driver, 10)
            matching_elements = wait.until(EC.visibility_of_any_elements_located((By.XPATH, xpath_pattern)))

            for element in matching_elements:
                span_str = element.find_element(By.XPATH, ".//div//span//div//span[contains(text(), '')]").text
                
                try:
                    parent_element = element.find_element(By.XPATH,  "./ancestor::*[1]")
                    parent_str = parent_element.find_element(By.XPATH, ".//div//span//div//span[contains(text(), '')]").text
                except:
                    pass

                if span_str not in clicked:
                    found = True
                    element.click()
                    clicked.add(span_str)
                    if parent_str != 'Content':
                        # We just opened a content chapter
                        element.click()
                        self.find_widgets(span_str)

                        


            if not found:
                break

    def find_widgets(self, span_str):
        print(span_str)

        xpath_pattern = "//*[contains(@class, 'widget')]"

        wait = WebDriverWait(self.driver, 10)
        widgets = wait.until(EC.visibility_of_any_elements_located((By.XPATH, xpath_pattern)))

        for widget in widgets:

            hover = ActionChains(self.driver).move_to_element(widget)
            hover.perform()
            print(widget.get_attribute('outerHTML'))
            widget.click()



        sleep(100)



    def __enter__(self):
        self.init_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        sleep(999)
        if self.driver:
            self.driver.quit()






if __name__ == '__main__':
      with Scraper() as scraper:
        scraper.log_in()
        scraper.click_on_course('College Algebra')
        scraper.expand_sidebar()
        #scraper.click_on_sidebar_submenu('Chapter 1')
        #scraper.list_sidebar()
