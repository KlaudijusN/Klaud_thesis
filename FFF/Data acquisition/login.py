from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time

#Login credentials
username = "Username"
password = "Password" 


#Initiate webdriver
driver = webdriver.Chrome() 

#Specify the url website and go to it
url = "https://www.eiger.io/signin"
driver.get(url)
time.sleep(3)

#Finding web page elements such as where is login and password, then type in the login credentials
driver.find_element_by_id("email").send_keys(username)
driver.find_element_by_id("Password").send_keys(password)
time.sleep(3)
#Selecting login button by XPath and clicking it
driver.find_element_by_xpath('//*[@id="signin-form"]/input[2]').click()
time.sleep(3)

#Going to the specific url where monitoring data is displayed
url_data = "https://www.eiger.io/device/e0d84087-f36b-45a5-9697-10954b872bad"
driver.get(url_data)
time.sleep(5)

