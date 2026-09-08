import time
from datetime import date, timedelta
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

driver = webdriver.Edge()
driver.get("http://127.0.0.1:8000")
time.sleep(2)
driver.maximize_window()

login_button = driver.find_element(by=By.CSS_SELECTOR, value='.button:nth-child(3)')
login_button.click()
time.sleep(5)





