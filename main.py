from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSd4xlS9RvzlFi8NXnZZvcVYJVyJiUEm" \
                  "_T7oNjtD29N6Tck67g/viewform?usp=sf_link"
zillow_url = "https://www.zillow.com/homes/for_rent/1-_beds/?searchQueryState=%7B%22pagination" \
             "%22%3A%7B%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-122.61529005957031%2C%22east%22%" \
             "3A-122.25136794042969%2C%22south%22%3A37.655249129677415%2C%22north%22%3A37.895139180" \
             "060085%7D%2C%22mapZoom%22%3A11%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7" \
             "B%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22fore" \
             "%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22auc%22%3A%7" \
             "B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value" \
             "%22%3Atrue%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%" \
             "3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D"

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}

web_page = requests.get(url=zillow_url, headers=header)
soup = BeautifulSoup(web_page.content, "html.parser")

prices_response = soup.select(selector="#grid-search-results .list-card-price")
addresses_response = soup.select(selector="#grid-search-results .list-card-addr")
links_response = soup.select(selector="#grid-search-results .list-card-top a")
links_response.pop()

all_prices = [price.getText().split("+")[0].split('/')[0] for price in prices_response]
all_addresses = [address.getText().split(" | ")[-1] for address in addresses_response]
all_links = [
    link.get("href")
    if "https" in link.get("href")
    else f"https://www.zillow.com{link.get('href')}"
    for link in links_response
]

time.sleep(3)

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get(google_form_url)

for index in range(len(all_links)):
    time.sleep(3)
    enter_address = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/'
                                                 'div[2]/div/div[1]/div/div[1]/input'
                                        )
    enter_address.send_keys(all_addresses[index])

    enter_price = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]'
                                               '/div/div[1]/div/div[1]/input'
                                      )
    enter_price.send_keys(all_prices[index])

    enter_link = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]'
                                              '/div/div[1]/div/div[1]/input'
                                     )
    enter_link.send_keys(all_links[index])

    submit_form = driver.find_element("xpath", '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span')
    submit_form.click()

    time.sleep(5)

    try:
        submit_new_response = driver.find_element("link text", 'Submit another response')
        submit_new_response.click()
    except NoSuchElementException:
        time.sleep(3)
        submit_new_response = driver.find_element("link text", 'Submit another response')
        submit_new_response.click()

time.sleep(5)
driver.quit()
