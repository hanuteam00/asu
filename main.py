import undetected_chromedriver as uc
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from vivchain import Agent

# Dòng này nạp biến môi trường từ tệp .env vào trong mã.
load_dotenv()

# Support Class: Các hàm này là hàm in tùy chỉnh để hiển thị văn bản màu sắc trên cửa sổ console để dễ nhìn hơn.
def print_in_red(s):
     print(f'\x1b[0;37;41m{s}\x1b[0m')

def print_in_blue(s):
     print(f'\x1b[0;37;44m{s}\x1b[0m')

def print_in_green(s):
     print(f'\x1b[0;37;42m{s}\x1b[0m')

"""
Lớp này đóng gói chức năng của scraper web. Nó bao gồm các phương thức để
- khởi tạo trình duyệt
- đăng nhập
- tương tác với các khóa học
- tương tác với thanh bên
- gửi tin nhắn
- xử lý cuộc trò chuyện với MathGPT.
"""
class Scraper:
    """
    # Nó được sử dụng để khởi tạo các thuộc tính của đối tượng
    # đảm bảo rằng mỗi đối tượng được tạo từ lớp này sẽ có các thuộc tính cơ bản được khởi tạo và có sẵn để sử dụng
    constructor() {
        this.driver = null;
        this.baseUrl = "https://poc.mathgpt.ai/";
    }
    """
    def __init__(self):
        # self.base_url được khởi tạo trong constructor __init__. Nếu bạn muốn sử dụng nó trong các phương thức khác của lớp, bạn có thể thực hiện việc này
        # self.driver = None
        self.base_url = 'https://poc.mathgpt.ai/'
        # self.base_url = 'https://google.com.vn'
        # pass
    

    # - khởi tạo trình duyệt
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
    
    """
    def scrape(self):
        # url = 'https://poc.mathgpt.ai/'
        url = 'https://google.com.vn'
        self.driver.get(url)
        html = self.driver.page_source
        print("html: " +html)
        """
    def scrape(self):
        pass

    # - đăng nhập
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

    # - tương tác với các khóa học
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
                    sleep(2)
                    get_started_button.click()
                    break
                except Exception as e:
                    print(f"Found course error: Error finding or clicking 'Get Started' button: {e}")

    # - tương tác với thanh bên
    def click_on_sidebar_submenu(self, span_str):

        xpath = f"//*[contains(@class, 'SidebarSubItemWrapper')]//span//div//span[contains(text(), '{span_str}')]/ancestor::*[contains(@class, 'SidebarSubItemWrapper')][1]"
        content_menu_item = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

        #print(content_menu_item.get_attribute('outerHTML'))
        #self.driver.execute_script("arguments[0].style.border='3px solid red'", content_menu_item)

        sleep(2)
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
                    sleep(2)
                    element.click()
                    clicked.add(span_str)
                    if parent_str != 'Content':
                        # We just opened a content chapter
                        sleep(2)
                        element.click()
                        for widget in self.find_widgets(span_str):

                            self.chat_with_mathgpt()


            if not found:
                break

    def wait_for_bot_to_type(self):

        # Wait for Skip Generating to show up and be dismissed
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//span[text()='Skip Generating']")))
        wait = WebDriverWait(self.driver, 30)
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//span[text()='Skip Generating']")))
        sleep(1)


    # - gửi tin nhắn
    def send_to_bot(self, message):
        editor_xpath = "//div[@contenteditable='true']"

        # Wait for the editor to be visible and ready for input
        wait = WebDriverWait(self.driver, 10)
        editor = wait.until(EC.visibility_of_element_located((By.XPATH, editor_xpath)))

        for m in message.split('\n'):
            editor.send_keys(m)
            editor.send_keys(Keys.SHIFT, Keys.ENTER)
        sleep(1)


        send_button_xpath = "//div[@data-name='send-button-icon']"

        # Wait for the send button to be clickable
        wait = WebDriverWait(self.driver, 10)
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, send_button_xpath)))

        # Click the send button
        send_button.click()

    # - xử lý cuộc trò chuyện với MathGPT - 1
    def get_chat_history(self):

        chat_history = []

        wait = WebDriverWait(self.driver, 10)
        chat_list = wait.until(EC.visibility_of_element_located((By.ID, "chat-list")))

        messages = chat_list.find_elements(By.XPATH, ".//div[@data-name]")

        for message in messages:
            message_type = 'TEACHER' if message.get_attribute('data-name').startswith('bot') else 'STUDENT'
            text = ' '.join(p.text for p in message.find_elements(By.TAG_NAME, 'p'))
            if not text:
                continue

            chat_history.append({'role': message_type, 'content': text})

        return chat_history

    ## - xử lý cuộc trò chuyện với MathGPT - 2
    def chat_with_mathgpt(self):
        print("Chatting - chat_with_mathgpt")
        self.wait_for_bot_to_type()
        response = self.get_chat_history()[-1]
        print_in_blue(response)

        student_prompt = \
"""
You are roleplaying as an algebra student. Act like a realistic teenager. Act like you are stuck. Be confused.
Don't be too helpful. And get some questions wrong. Give your teacher incomplete information.
Don't type too much. Let your teacher guide you.

Act like a student!
"""
        student_functions = []
        student_agent = Agent(
            system_prompt=student_prompt,
            functions=student_functions,
            model='gpt-4-0125-preview',
            use_CI=False
        )

        for _ in range(3):
            response = student_agent.submit(response['content'])
            print_in_green(response)
            sleep(1)
            self.send_to_bot(response)
            sleep(1)
            self.wait_for_bot_to_type()
            response = self.get_chat_history()[-1]
            print_in_blue(response)
            sleep(1)


        entire_chat = self.get_chat_history()

        sleep(2)

        clean_up = self.driver.find_element(By.ID, "cleanup-button")
        clean_up.click()


        sleep(1)


    def find_widgets(self, span_str):
        print(span_str)

        xpath_pattern = "//*[contains(@class, 'widget') and not(contains(@class, 'widget-overlay'))]"


        wait = WebDriverWait(self.driver, 10)
        #widgets = wait.until(EC.visibility_of_any_elements_located((By.XPATH, xpath_pattern)))
        sleep(1)
        widgets = self.driver.find_elements(By.XPATH, xpath_pattern)

        for widget in widgets:
            widget_type = widget.get_attribute("data-widget-type")
            if widget_type == "link":
                continue

            hover = ActionChains(self.driver).move_to_element(widget)
            hover.perform()
            sleep(1)
            widget.click()
            sleep(1)

            dropdown = self.driver.find_element(By.ID, "activity-dropdown")
            ask_question_option = dropdown.find_element(By.XPATH, "//div[@id='activity-dropdown']//div[@role='button' and contains(., 'Ask a Question')]")
            ask_question_option.click()

            yield
  


        #print('sleeping')
        #sleep(100)


    #
    def __enter__(self):
        self.init_browser()
        return self

    # 
    def __exit__(self, exc_type, exc_val, exc_tb):

        sleep(999)
        if self.driver:
            self.driver.quit()
    
"""
Kịch bản đi vào khối chính, nơi nó tạo một phiên bản của lớp Scraper và thực hiện một chuỗi các hành động như
- đăng nhập, 
- nhấp vào một khóa học và
- mở rộng thanh bên. 
Câu lệnh with đảm bảo sự khởi tạo và làm sạch đúng đắn của tài nguyên bằng cách
sử dụng các phương thức __enter__ và __exit__ trong lớp Scraper.
"""
if __name__ == '__main__':
      with Scraper() as scraper:
        scraper.log_in()
        scraper.click_on_course('Manh_College Algebra')
        scraper.expand_sidebar()
        #scraper.click_on_sidebar_submenu('Chapter 1')
        #scraper.list_sidebar()
