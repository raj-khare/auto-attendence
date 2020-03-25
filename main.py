from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from os import path
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pickle
import datetime


def get_credentials():
    print("Loading credentials...")
    if not path.exists("credentials.p"):
        username = input("Enter your Registration no.: ")
        password = input("Enter your password: ")
        roll = input("Enter your roll no: ")
        pickle.dump({'username': username, 'password': password, 'roll': roll},
                    open("credentials.p", "wb"))
        return username, password, roll
    credentials = pickle.load(open("credentials.p", "rb"))
    return credentials['username'], credentials['password'], credentials['roll']


def get_time_table(driver, username, password):
    print("Extracting time table...")

    def extract_time_table():
        driver.get("https://ums.lpu.in/lpuums/")
        driver.find_element_by_class_name("input_type").send_keys(username)
        driver.find_element_by_class_name("login_box").click()
        driver.find_element_by_class_name(
            "input_type_pass").send_keys(password)
        Select(driver.find_element_by_id(
            "ddlStartWith")).select_by_index(1)
        driver.find_element_by_id("iBtnLogins").click()
        table = driver.find_element_by_class_name("table-hover")
        rows = table.find_elements_by_tag_name("tr")
        time_table = {}
        for row in rows:
            _data = row.find_elements_by_tag_name("td")
            time, course = _data[0].text, _data[1].text
            time_table[time] = course

        time_table['date'] = datetime.date.today()
        pickle.dump(time_table, open("timetable.p", "wb"))
        return time_table

    if path.exists("timetable.p"):
        time_table = pickle.load(open("timetable.p", "rb"))
        if time_table['date'] == datetime.date.today():
            return time_table
    return extract_time_table()


def get_current_class(time_table):
    print("Getting current class...")
    now = datetime.datetime.now()
    hour = now.hour
    if hour != 12:
        hour = hour % 12
    for time, course in time_table.items():
        if time != "date":
            if int(time[:2]) < hour + 0.5 < int(time[3:5]):
                print(f"\nCURRENT CLASS: {course} {(time)}\n")
                return course


if __name__ == "__main__":
    driver = webdriver.Chrome(executable_path="./chromedriver")
    try:
        username, password, roll = get_credentials()
        time_table = get_time_table(driver, username, password)
        course = get_current_class(time_table)
        driver.get("https://lpulive.lpu.in/login")
        driver.find_element_by_id("inputEmail").send_keys(username)
        password = driver.find_element_by_id(
            "inputPassword").send_keys(password)
        driver.find_element_by_tag_name("button").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "chat-input"))
        )
        courses = driver.find_elements_by_css_selector(".conv-label")
        for c in courses:
            if course in c.text:
                c.click()
                text_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "chat-input"))
                )
                text_box.send_keys(f"Roll no. {roll}")
                print("Attendence marked!")
                time.sleep(10)
    except Exception as e:
        print(e)
    finally:
        driver.close()
