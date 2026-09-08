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
time.sleep(2)

select_doctor_input = driver.find_element(By.ID, 'doctorSelect')
select_doctor_input.click()

combobox = Select(select_doctor_input)
combobox.select_by_index(2)
select_doctor_input.click()
time.sleep(5)

select_date_input = driver.find_element(By.ID, 'dateInput')

data_amanha = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

driver.execute_script("arguments[0].value = arguments[1];", select_date_input, data_amanha)
sleep(2)
select_hour_input = driver.find_element(By.CSS_SELECTOR, '.slot-button:nth-child(1)')
select_hour_input.click()
time.sleep(1)

submit_shedule_button = driver.find_element(By.ID, 'appointmentSubmit')
submit_shedule_button.click()
sleep(2)
reshedule_button = driver.find_element(By.CSS_SELECTOR, '.small-button:nth-child(1)')
sleep(2)
reshedule_button.click()
sleep(2)
update_hour_button = driver.find_element(By.CSS_SELECTOR, '.slot-button:nth-child(1)')
sleep(2)
update_hour_button.click()
sleep(2)
submit_shedule_button.click()
sleep(5)





