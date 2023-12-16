from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()

prefs = {"download.default_directory" : r"C:\Users\James\Github\TFBAttent\TFBAttent\script_results"}

# create a new Edge browser instance
driver = webdriver.Chrome()

# navigate to your web app
driver.get(r'https://rohslab.cmb.usc.edu/DNAshape/index.html')

# open your file
with open(r'C:\Users\James\Github\TFBAttent\TFBAttent\data\positives\CTCF_positive_regions_trimmed_fix.txt.fa', 'r') as file:
    lines = file.readlines()

# find the input element (replace 'inputElementName' with the name of your input element)
inputElement = driver.find_element(By.NAME, 'sequence')
submitElement = driver.find_element(By.XPATH,'//*[@id="form1"]/input[1]')

# iterate over the lines in the file, inputting each one into the form
i =0
for line in lines:
    try:

        inputElement.send_keys(line)
        if i%100 == 1 and i != 0:
            
            submitElement.click()  # simulate clicking the submit button
            #driver.implicitly_wait(2)  # wait for the page to load
            downloadLink = driver.find_element(By.XPATH,'/html/body/div/div[2]/div[2]/div[2]/div[1]/a[2]')
            downloadLink.click()
        #   driver.implicitly_wait(2)  # wait for the page to load
            driver.back()
            clearElement = driver.find_element(By.XPATH,'//*[@id="form1"]/input[2]')
            clearElement.click()
        if i== len(lines)-1:
            submitElement.click()  # simulate clicking the submit button
            #driver.implicitly_wait(2)  # wait for the page to load
            downloadLink = driver.find_element(By.XPATH,'/html/body/div/div[2]/div[2]/div[2]/div[1]/a[2]')
            downloadLink.click()
        #   driver.implicitly_wait(2)  # wait for the page to load
            driver.back()
            clearElement = driver.find_element(By.XPATH,'//*[@id="form1"]/input[2]')
            clearElement.click()
            print("Done" + str(i-25) + "-" +str(i))
    except:
        print("Error on line " + str(i))
    i+=1
# close the browser
driver.close()