import json
import os
import asyncio
import aiohttp
import urllib
from uc import undetected_chromedriver as  webdriver
import re
import httpx
import imgkit
from html2image import Html2Image
import base64
from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import string
import random
import subprocess
import time
import requests
import pandas as pd
from flask import Flask, request, jsonify
import threading
import queue
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
app = Flask(__name__)
# Queue to handle requests
request_queue = queue.Queue()
import psutil
import os
def memory_limiter(max_memory, check_interval=1):
    """
    Continuously check the memory usage of the current process and
    kill it if it exceeds max_memory (in megabytes).
    """
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / (1024 * 1024)  # Memory usage in MB
        if mem > max_memory:
            process.kill()
        time.sleep(check_interval)

def ensure_chromedriver():
    # Check if chromedriver exists in the current directory
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
    if not os.path.exists(chromedriver_path):
        # If not found, use webdriver_manager to download/install it
        chromedriver_path = ChromeDriverManager().install()
    else:
        # If found, check version compatibility
        installed_chrome_version = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True).stdout.strip().split()[-1].split('.')[0]
        chromedriver_version = subprocess.run([chromedriver_path, '--version'], capture_output=True, text=True).stdout.strip().split()[1].split('.')[0]
        
        # If major version mismatch, re-download matching chromedriver
        if installed_chrome_version != chromedriver_version:
            chromedriver_path = ChromeDriverManager().install()
    
    return chromedriver_path
async def get_domains_logos(domains):
    async def fetch_logo_url(session, domain):
        url = f'https://besticon-demo.herokuapp.com/allicons.json?url={domain}'
        async with session.get(url) as response:
            try:
                json_data = await response.json()
                icon_url = json_data['icons'][0]['url']
                return {'domain': domain ,'image': icon_url}
            except Exception:
                return {'domain': domain ,'image': ''}
    async def fetch_all_logos_urls():
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_logo_url(session, domain) for domain in domains]
            return await asyncio.gather(*tasks)
    logos = await (fetch_all_logos_urls())
    return logos
def scraper_function(link, result_queue):
    try:  
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        # Limit cache size
        options.add_argument("--disk-cache-size=1")       

        options.add_argument("--disable-gpu")   
        options.add_argument("--prerender-from-omnibox=disabled")    
        options.add_argument("--disable-software-rasterizer")
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.headless = True

        options.add_experimental_option("prefs", prefs)

        windows_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        scraped_data = {}
        simplyweb={}
        options.add_argument(f"--user-agent={windows_user_agent}")
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--load-extension=SimplyTrends')

        browser = webdriver.Chrome(options=options,version_main=122)


        cookies_file = 'cookies_simpletrends.json'
        try:

            browser.get(link)

            # cookies = browser.get_cookies()
            # print("Cookies from first site:", cookies)
            # with open(cookies_file, 'w') as file:
            #   json.dump(cookies, file)
            # print("Cookies saved to file.")
            # browser.delete_all_cookies()
            #
            #  # Apply each cookie
            # for cookie in cookies:
            #      browser.add_cookie(cookie)

            with open(cookies_file, 'r') as file:
                cookies = json.load(file)

            # Clear existing cookies in the browser
            browser.delete_all_cookies()

            # Add new cookies
            for cookie in cookies:
                browser.add_cookie(cookie)
            # Open the second website
            print('done')

            # Refresh the page to apply cookies
            #browser.refresh()
            # browser.get('https://app.simplytrends.co/shopifystore/barnerbrand.com')
            browser.get(link)
            domain = WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#appBarContainer > div > div > p > p > a.MuiTypography-root.MuiTypography-inherit.MuiLink-root.MuiLink-underlineHover.css-1xa0emq > p')))
            domain_name = domain.text
            dot_position = domain_name.find('.')

            # Extract the text from the dot position to the end of the string
            extension = domain_name[dot_position:] if dot_position != -1 else ''

            print(extension)
            scraped_data['domain_name'] = domain.text
            # icon = WebDriverWait(browser, 0.5).until(
            #     EC.presence_of_element_located((By.XPATH,
            #                                     '/html/body/div[1]/header/div[2]/div[2]/div/div/div/div/div[1]/div/img')))
            # icon=icon.get_attribute('src')
            #icon = asyncio.run(get_domains_logos(link))['image']
            link1 = link
            link1 = link1.replace("https://app.simplytrends.co/shopifystore/", "")
            link1 = link1.split('?')[0]

            url = f'https://besticon-demo.herokuapp.com/allicons.json?url={link1}'
            print(url)
            try:
                with urllib.request.urlopen(url) as response:
                    json_data = json.loads(response.read().decode('utf-8'))
                    icon_url = json_data['icons'][0]['url']
                    print(icon_url)
                    #return {'domain': domain, 'image': icon_url}
                    scraped_data['icon'] = icon_url

            except urllib.error.URLError as e:
                scraped_data['icon'] = " "
                
                
            try:
             monthlyunites = WebDriverWait(browser, 3).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div/div/p')))
             monthlyunites = monthlyunites.text
            except:
                monthlyunites='-'
            print(monthlyunites)
            scraped_data['monthlyunites'] = monthlyunites

            try:
                monthlyrevenue = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/p')))
                monthlyrevenue = monthlyrevenue.text
            except Exception as e:
                monthlyrevenue = '-'
            print(monthlyrevenue)
            scraped_data['monthlyrevenue'] = monthlyrevenue

            try:
                storename = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div/div/div[3]/div/div/p[1]')))
                storename = storename.text
            except Exception as e:
                storename = '-'
            print(storename)
            scraped_data['storename'] = storename
            try:
                categoryyrank = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(5) > div > div > div > div > p')))
                categoryyrank = categoryyrank.text
            except:
                categoryyrank = "-"
            print(categoryyrank)
            scraped_data['categoryyrank'] = categoryyrank

            try:
                country = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(1) > div > div > div > div > p > div > span')))
                country = country.text
            except Exception as e:
                country = '-'
            print(country)
            scraped_data['country'] = country

            try:
                countryrank = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[3]/div/div/div[1]/div[4]/div/div/div/div/p')))
                countryrank = countryrank.text
            except:
                countryrank = "-"
            print(countryrank)
            scraped_data['countryrank'] = countryrank
            try:
                socialmedia = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '//*[@id="__next"]/div/div[2]/div/div/div/div/div[3]/div/div/div[2]')))
                links = socialmedia.find_elements(By.TAG_NAME, 'a')

                # Initialize an empty list to store href values
                hrefs = []

                # Iterate through found links and get the 'href' attribute
                for link in links:
                    href = link.get_attribute('href')
                    if href:  # Ensure href is not None
                        hrefs.append(href)
            except:
                href = "-"
            print("Extracted URL:", hrefs)
            scraped_data['socialmedia'] = hrefs
            try:
                monthstats = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > h2 > span > p > div')))
                monthstats = monthstats.text
            except Exception as e:
                monthstats = '-'
            print(monthstats)
            scraped_data['monthstats'] = monthstats
            try:
             visible_owerview = WebDriverWait(browser, 0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div')))
            except:
                visible_owerview='-'

            print(visible_owerview.text)
            scraped_data['visible_owerview'] = visible_owerview.text

            start_keyword = "Country rank"
            end_keyword = "Category rank"
            text = visible_owerview.text

            # Find start and end positions
            start_pos = text.find(start_keyword)
            end_pos = text.find(end_keyword)
            result = []

            # Check if both keywords are found
            if start_pos != -1 and end_pos != -1:
                # Extract the relevant part of the string
                relevant_part = text[start_pos + len(start_keyword):end_pos].strip()

                # Split the string into a list at every newline and remove empty strings
                result = [line for line in relevant_part.split('\n') if line]
            print(result)
            if(visible_owerview=='-'):
                scraped_data['Country_rank'] = '-'
            else:
             scraped_data['Country_rank'] = result

            start_keyword = "Category rank"
            end_keyword = "Global rank"
            text = visible_owerview.text

            # Find start and end positions
            start_pos = text.find(start_keyword)
            end_pos = text.find(end_keyword)
            result = []

            # Check if both keywords are found
            if start_pos != -1 and end_pos != -1:
                # Extract the relevant part of the string
                relevant_part = text[start_pos + len(start_keyword):end_pos].strip()

                # Split the string into a list at every newline and remove empty strings
                result = [line for line in relevant_part.split('\n') if line]
            print(result)
            if (visible_owerview == '-'):
                scraped_data['Category_rank'] = '-'
            else:
                scraped_data['Category_rank'] = result


            start_keyword = "Global rank"
            end_keyword = "Social media"
            text = visible_owerview.text

            # Find start and end positions
            start_pos = text.find(start_keyword)
            end_pos = text.find(end_keyword)
            result = []

            # Check if both keywords are found
            if start_pos != -1 and end_pos != -1:
                # Extract the relevant part of the string
                relevant_part = text[start_pos + len(start_keyword):end_pos].strip()

                # Split the string into a list at every newline and remove empty strings
                result = [line for line in relevant_part.split('\n') if line]
            print(result)
            if (visible_owerview == '-'):
                scraped_data['Global_rank'] = '-'
            else:
                scraped_data['Global_rank'] = result

            try:
                language = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(2) > div > div > div > div > p')))
                language = language.text
            except Exception as e:
                language = '-'
            print(language)
            scraped_data['language'] = language

            try:
                currency = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(3) > div > div > div > div > p')))
                currency = currency.text
            except Exception as e:
                currency = '-'
            print(currency)
            scraped_data['currency'] = currency

            try:
                firstpublishproduct = WebDriverWait(browser, 0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > div:nth-child(3) > div:nth-child(1) > div > div > div > div > p')))
                firstpublishproduct = firstpublishproduct.text
            except Exception as e:
                firstpublishproduct = '-'
            print(firstpublishproduct)
            scraped_data['firstpublishproduct'] = firstpublishproduct

            try:
                lastpublishproduct = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > div:nth-child(3) > div:nth-child(2) > div > div > div > div > p')))
                lastpublishproduct = lastpublishproduct.text
            except Exception as e:
                lastpublishproduct = '-'
            print(lastpublishproduct)
            scraped_data['lastpublishproduct'] = lastpublishproduct

            try:
                numproducts = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > div:nth-child(3) > div:nth-child(3) > div > div > div > div > p')))
                numproducts = numproducts.text
            except Exception as e:
                numproducts = '-'
            print(numproducts)
            scraped_data['numproducts'] = numproducts

            try:
                avgprices = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]/div[4]/div/div/div/div/p')))
                avgprices = avgprices.text
            except Exception as e:
                avgprices = '-'
            print(avgprices)
            scraped_data['avgprices'] = avgprices

            try:
                highestproductprice = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]/div[5]/div/div/div/div/p')))
                highestproductprice = highestproductprice.text
            except Exception as e:
                highestproductprice = '-'
            print(highestproductprice)
            scraped_data['highestproductprice'] = highestproductprice

            try:
                lowestproductprice = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]/div[6]/div/div/div/div/p')))
                lowestproductprice = lowestproductprice.text
            except Exception as e:
                lowestproductprice = '-'
            print(lowestproductprice)
            scraped_data['lowestproductprice'] = lowestproductprice

            try:
                ch = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[3]/div/div/div/div/div[8]/p'))).click()
                ch = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div')))
            except:
                ch = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[3]')))
                pass
            time.sleep(1)

            div_html = ch.get_attribute('innerHTML')

            soup = BeautifulSoup(div_html, 'html.parser')

            # Define a list to hold all the rows of data
            data = []

            vendor_divs = soup.find_all('div', class_='css-69i1ev')

            # Loop through the vendor divs to extract the data
            for vendor in vendor_divs:
                # Extract the vendor name

                # time.sleep(30)
                # vendor_name = vendor.find('a').get_text(strip=True)
                # distribution_span = vendor.find('span')
                distribution_span = vendor.find('a', class_='css-1xa0emq')
                vender_span = vendor.find('div', class_='css-1vtkzp1')
                vendor_name = vender_span.find('span').get_text(strip=True) if distribution_span else 'Unknown'

                # Extract the distribution percentage
                # distribution_span = vendor.parent.find('span', class_='css-15nru74')
                spans = vendor.parent.find_all('span', class_='css-15nru74')

                # Select the span you want by index, e.g., the second span
                if len(spans) > 1:
                    desired_span = spans[1]  # This is the second span
                    # Now you can extract the text or any other attribute from the desired_span
                    distribution = desired_span.get_text(strip=True)
                else:
                    distribution = 'N/A'
                # distribution_span = distribution_span.find_next_sibling('span', class_='css-15nru74')
                # distribution = distribution_span.get_text(strip=True) if distribution_span else 'Unknown'

                # Extract the number of products. It's in the next div with class 'css-18jpfvm'
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').get_text(strip=True)
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').find('p').get_text(strip=True)
                num_products_div = vendor.parent.find_next_sibling('div', class_='css-18jpfvm')
                num_products = num_products_div.find('p').get_text(
                    strip=True) if num_products_div else 'Unknown'

                # Append the data to the list
                data.append({'Vendor': vendor_name, 'Distribution': distribution,
                             'Number of products': num_products})

            # Create a DataFrame

            df = pd.DataFrame(data)

            # Print the DataFrame
            print(df)
            scraped_data['Vendor_table'] = data
            try:
                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/button'))).click()
            except:
                pass

            try:

             click = WebDriverWait(browser,0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[6]/div/div/div/div/div/div[8]/p'))).click()

             click = WebDriverWait(browser,0.5).until(
                 EC.presence_of_element_located((By.XPATH,
                                                 '/html/body/div[3]/div[3]/div/div/div')))
            except:

                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[5]/div/div/div')))
                pass

            #time.sleep(0.5)


            div_html = click.get_attribute('innerHTML')

            soup = BeautifulSoup(div_html, 'html.parser')

            # Define a list to hold all the rows of data
            data_producttags = []

            vendor_divs = soup.find_all('div', class_='css-1dogkm')

            # Loop through the vendor divs to extract the data


            c=0
            for vendor in vendor_divs:
                # Extract the vendor name
                distribution_span = vendor.find('a', class_='css-1xa0emq')
                vender_span = vendor.find('div', class_='css-1vtkzp1')
                vendor_name = vender_span.find('span').get_text(strip=True) if distribution_span else 'Unknown'

                # Extract the distribution percentage
                # distribution_span = vendor.parent.find('span', class_='css-15nru74')
                spans = vendor.parent.find_all('span', class_='css-15nru74')

                # Select the span you want by index, e.g., the second span
                if len(spans) > 1:
                    desired_span = spans[1]  # This is the second span
                    # Now you can extract the text or any other attribute from the desired_span
                    distribution = desired_span.get_text(strip=True)
                else:
                    distribution = 'N/A'
                # distribution_span = distribution_span.find_next_sibling('span', class_='css-15nru74')
                # distribution = distribution_span.get_text(strip=True) if distribution_span else 'Unknown'

                # Extract the number of products. It's in the next div with class 'css-18jpfvm'
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').get_text(strip=True)
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').find('p').get_text(strip=True)
                num_products_div = vendor.parent.find_next_sibling('div', class_='css-18jpfvm')
                num_products = num_products_div.find('p').get_text(
                    strip=True) if num_products_div else 'Unknown'





                # Extract the number of products. It's in the next div with class 'css-18jpfvm'
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').get_text(strip=True)
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').find('p').get_text(strip=True)


                # Append the data to the list
                data_producttags.append({'Product_tag': vendor_name, 'Distribution': distribution,
                                         'Number of products': num_products})
                c+=1
                if(c>5):
                    break

            # Create a DataFrame

            df_producttags = pd.DataFrame(data_producttags)

            # Print the DataFrame
            print(df_producttags)
            scraped_data['df_producttags'] = data_producttags
            try:
                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/button'))).click()
            except:
                pass
            try:
                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[5]/div/div/div/div/div/div[8]/p'))).click()
                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/div')))
            except:
                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[6]/div/div/div')))
                pass



            div_html = click.get_attribute('innerHTML')

            soup = BeautifulSoup(div_html, 'html.parser')

            # Define a list to hold all the rows of data
            data_producttyps = []

            vendor_divs = soup.find_all('div', class_='css-fb4b82')

            # Loop through the vendor divs to extract the data
            for vendor in vendor_divs:
                # Extract the vendor name
                distribution_span = vendor.find('a', class_='css-1xa0emq')
                vender_span = vendor.find('div', class_='css-1vtkzp1')
                vendor_name = vender_span.find('span').get_text(strip=True) if distribution_span else 'Unknown'

                # Extract the distribution percentage
                # distribution_span = vendor.parent.find('span', class_='css-15nru74')
                spans = vendor.parent.find_all('span', class_='css-15nru74')

                # Select the span you want by index, e.g., the second span
                if len(spans) > 1:
                    desired_span = spans[1]  # This is the second span
                    # Now you can extract the text or any other attribute from the desired_span
                    distribution = desired_span.get_text(strip=True)
                else:
                    distribution = 'N/A'
                # distribution_span = distribution_span.find_next_sibling('span', class_='css-15nru74')
                # distribution = distribution_span.get_text(strip=True) if distribution_span else 'Unknown'

                # Extract the number of products. It's in the next div with class 'css-18jpfvm'
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').get_text(strip=True)
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').find('p').get_text(strip=True)
                num_products_div = vendor.parent.find_next_sibling('div', class_='css-18jpfvm')
                num_products = num_products_div.find('p').get_text(
                    strip=True) if num_products_div else 'Unknown'

                # Append the data to the list
                data_producttyps.append({'Product_type': vendor_name, 'Distribution': distribution,
                                         'Number of products': num_products})

            df_producttags = pd.DataFrame(data_producttyps)

            # Print the DataFrame
            print(df_producttags)
            scraped_data['df_producttype'] = data_producttyps
            try:
                click = WebDriverWait(browser,0.5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/button'))).click()
            except:
                pass

            click = WebDriverWait(browser,0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/header/div[2]/div[2]/div/div/div/nav/div/div/div/div[1]/button[3]'))).click()
            visible_traffic = WebDriverWait(browser,0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div/div')))

            print(visible_traffic.text)
            scraped_data['visible_traffic'] = visible_traffic.text
            try:
                try:
                    monthlyvisits = WebDriverWait(browser, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div > div > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div > div > p.MuiTypography-root.MuiTypography-h6.css-1krdksj')))
                    monthlyvisits = monthlyvisits.text
                except Exception as e:
                    monthlyvisits = '-'
                print(monthlyvisits)
                scraped_data['monthlyvisits'] = monthlyvisits

                try:
                    avgvisitduration = WebDriverWait(browser,0.5).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '/html/body/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/p')))
                    avgvisitduration = avgvisitduration.text
                except Exception as e:
                    avgvisitduration = '-'
                print(avgvisitduration)
                scraped_data['avgvisitduration'] = avgvisitduration

                try:
                    pagespervisit = WebDriverWait(browser,0.5).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '/html/body/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[3]/div/div/div/div/p')))
                    pagespervisit = pagespervisit.text
                except Exception as e:
                    pagespervisit = '-'
                print(pagespervisit)
                scraped_data['pagespervisit'] = pagespervisit

                try:
                    bouncertate = WebDriverWait(browser,0.5).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        '/html/body/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[4]/div/div/div/div/p')))
                    bouncertate = bouncertate.text
                except Exception as e:
                    bouncertate = '-'
                print(bouncertate)
                scraped_data['bouncertate'] = bouncertate

                click = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div > div > div > div:nth-child(2) > div > div > div:nth-child(2) > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-4.css-z6jnb7 > div > div')))

                div_html = click.get_attribute('innerHTML')

                soup = BeautifulSoup(div_html, 'html.parser')

                # Define a list to hold all the rows of data
                data_countryvisits = []

                country_divs = soup.find_all('div', class_='css-1wgohow')

                for div in country_divs:
                    # Extracting the country name and visit percentage
                    country_name = div.find('p', class_='MuiTypography-root').get_text(strip=True)
                    visit_percentage = div.find_all('p', class_='MuiTypography-root')[-1].get_text(strip=True)

                    data_countryvisits.append({'Country_Name': country_name, 'Visits_percentage': visit_percentage})

                print(data_countryvisits)
                scraped_data['data_countryvisits'] = data_countryvisits

                click = WebDriverWait(browser, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    'g.recharts-layer.recharts-label-list')))

                div_html = click.get_attribute('innerHTML')

                soup = BeautifulSoup(div_html, 'html.parser')

                # Define a list to hold all the rows of data
                socialmediatraffic = []

                vendor_divs = soup.find_all('text', class_='recharts-text')

                # Loop through the vendor divs to extract the data
                for vendor in vendor_divs:
                    # Extracting the age group and percentage
                    age_group = vendor['name']
                    percentage = vendor.find('tspan').get_text(strip=True)

                    # Append the data to the list
                    socialmediatraffic.append({age_group: percentage})

                print(socialmediatraffic)
                scraped_data['socialmediatraffic'] = socialmediatraffic

                click = WebDriverWait(browser, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    'g.recharts-layer.recharts-pie-labels')))

                div_html = click.get_attribute('innerHTML')

                soup = BeautifulSoup(div_html, 'html.parser')

                # Define a list to hold all the rows of data

                # Find all 'g' tags under the main 'recharts-pie-labels' class
                label_groups = soup.find_all('g', class_='recharts-layer', recursive=False)

                data_malefepercent = []
                
                # Extracting the percentages
                na=['female','male']
                label_name = ''
                percentage = ''
                # Extracting the percentages
                c=0
                for group in label_groups:
                    text_element = group.find('text')
                    if text_element:
                        percentage = text_element.get_text(strip=True)
                    path_element = group.find_previous_sibling('path')

                    label_name = na[c]
                    c+=1
                    data_malefepercent.append({label_name: percentage})

                print(data_malefepercent)
                scraped_data['data_malefepercent'] = data_malefepercent
                try:
                    click = WebDriverWait(browser,0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div > div > div > div:nth-child(3) > div > div > div > div > div > div > svg > g:nth-child(3) > g.recharts-layer.recharts-label-list')))

                    div_html = click.get_attribute('innerHTML')

                    soup = BeautifulSoup(div_html, 'html.parser')

                    # Define a list to hold all the rows of data
                    agrgroup = []

                    vendor_divs = soup.find_all('text', class_='recharts-text')

                    # Loop through the vendor divs to extract the data
                    for vendor in vendor_divs:
                        # Extracting the age group and percentage
                        age_group = vendor['name']
                        percentage = vendor.find('tspan').get_text(strip=True)

                        # Append the data to the list
                        agrgroup.append({age_group: percentage})

                    print(agrgroup)
                    scraped_data['agrgroup'] = agrgroup
                except:
                    pass
            except:
                pass
            click = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/header/div[2]/div[2]/div/div/div/nav/div/div/div/div[1]/button[4]'))).click()
            time.sleep(1)
            visible_text_tech = WebDriverWait(browser,0.5).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]')))

            print(visible_text_tech.text)
            scraped_data['visible_text_tech'] = visible_text_tech.text
            start_keyword = "processors"
            end_keyword = "Reviews"
            text= scraped_data['visible_text_tech']

            # Find start and end positions
            start_pos = text.find(start_keyword)
            end_pos = text.find(end_keyword, start_pos + len(start_keyword))
            result=[]

            # Check if both keywords are found
            if start_pos != -1 and end_pos != -1:
                # Extract the relevant part of the string
                relevant_part = text[start_pos + len(start_keyword):end_pos].strip()

                # Split the string into a list at every newline and remove empty strings
                result = [line for line in relevant_part.split('\n') if line]
            print(result)
            scraped_data['payment_methods'] = result

            start_keyword = "Top 5 popular categories"
            end_keyword = "Top 5 hot topic"
            text =  scraped_data['visible_text_tech']

            # Find start and end positions
            start_pos = text.find(start_keyword)
            end_pos = text.find(end_keyword, start_pos + len(start_keyword))
            result = []

            # Check if both keywords are found
            if start_pos != -1 and end_pos != -1:
                # Extract the relevant part of the string
                relevant_part = text[start_pos + len(start_keyword):end_pos].strip()

                # Split the string into a list at every newline and remove empty strings
                result = [line for line in relevant_part.split('\n') if line]
            print(result)
            scraped_data['Top_5_popular_categories'] = result

            start_keyword = "Top 5 hot topic"
            end_keyword = "Other sites surveyed"
            text =  scraped_data['visible_text_tech']

            # Find start and end positions
            start_pos = text.find(start_keyword)
            end_pos = text.find(end_keyword, start_pos + len(start_keyword))
            result = []

            # Check if both keywords are found
            if start_pos != -1 and end_pos != -1:
                # Extract the relevant part of the string
                relevant_part = text[start_pos + len(start_keyword):end_pos].strip()

                # Split the string into a list at every newline and remove empty strings
                result = [line for line in relevant_part.split('\n') if line]
            print(result)
            scraped_data['Top_5_hot_topic'] = result

            
            
            
           


            browser.quit()
            try:
             os.system("pkill chromedriver")
            except:
                pass
            result_queue.put(scraped_data)

        except  Exception as e:
            print(a)
           

            pass





    except:
        print(a)
        browser.quit()
        print('exception')

    
def convertTuple(tup):

    strc = ''
    c = len(tup)

    for item in range(5):
        strc = strc + strc.join(tup[item])

    return strc


letters = string.ascii_lowercase




mobile_emulation = {"deviceName": "iPhone SE"}
# options.add_experimental_option("mobileEmulation", mobile_emulation)
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
# options.add_experimental_option("mobileEmulation", mobile_emulation)
count = 0
recount = 100
total = 0

from bs4 import BeautifulSoup
def find_first_link(text):
    # Regular expression pattern for finding URLs
    pattern = r'https?://\S+'
    match = re.search(pattern, text)
    return match.group(0) if match else None
def generate_random_username(length=10):
    all_characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    username = ''.join(random.choice(all_characters) for _ in range(length))
    return username
greetings = ["Hello", "Hi", "Hey", "Greetings", "Howdy"]
subjects = ["this article", "your post", "the blog", "the content", "this page"]
verbs = ["is amazing", "is interesting", "was enlightening", "is insightful", "is impressive"]
adverbs = ["really", "truly", "absolutely", "definitely", "certainly"]
compliments = ["great job", "excellent work", "fantastic read", "good stuff", "wonderful insight"]

def generate_comment():
    # Randomly pick parts of the sentence
    greeting = random.choice(greetings)
    subject = random.choice(subjects)
    verb = random.choice(verbs)
    adverb = random.choice(adverbs)
    compliment = random.choice(compliments)

    # Construct the comment
    comment = f"{greeting}, {subject} {verb}. {adverb} {compliment}!"
    return comment

def is_liked(soup_svg):
    return bool(soup_svg.find('clipPath', {'id': '__lottie_element_8932'}))


import threading
# Other imports remain the same

# Define the function that each thread will execute
def thread_function(cookies_file, file_path_follow, file_path_like, file_path_comment):
    try:
        options = webdriver.ChromeOptions()
        # ... (other options setup)

        browser = webdriver.Chrome(options=options)

        # Load cookies from the specified file
        with open(cookies_file, 'r') as file:
            cookies = json.load(file)
            for cookie in cookies:
                browser.add_cookie(cookie)
        browser.refresh()

        # Your existing logic for follow, like, and comment
        # ...
        # Make sure to use the file_path_follow, file_path_like, and file_path_comment variables
        # ...

        browser.quit()

    except Exception as e:
        print(str(e))
        browser.quit()

# Main execution


@app.route('/scrape', methods=['POST'])
def scrape():
    link = request.json.get('link')
    result_queue = queue.Queue()

    # Start a new thread for each scraping request
    try:
    
     thread = threading.Thread(target=scraper_function, args=(link, result_queue))
     thread.start()
     
    # Wait for the result
     try:
      result = result_queue.get(timeout=60)  # Adjust timeout as necessary
     except queue.Empty:
      # Handle the case where no result is produced within the timeout period
      print("Failed to get result from worker thread within timeout")
      return jsonify({'error': 'Timeout waiting for result'}), 504   
       
    except: 
        print(a)
        return 'again'

    return jsonify(result)

@app.route('/ScrapeProductsImages', methods=['POST'])
def ScrapeProductsImages():
    data = request.json
    search_term = data.get('search_term')
    url = 'https://www.google.com/search?q={0}&tbm=isch'.format(search_term)
    try:
        content = httpx.get(url).content
    except:
        return jsonify({"response":"Exception occured while requesting the resource from Google Images!"})
    soup = BeautifulSoup(content,'lxml')
    images = soup.findAll('img')
    products_urls = []
    for image in images:
        products_urls.append(image.get('src'))
    return jsonify(products_urls)
@app.route('/CaptureLandingPageScreenshot', methods=['POST'])
def CaptureLandingPageScreenshot():
    data = request.json
    domain = data.get('domain')
    try:
        url = 'https://'+domain
        img = imgkit.from_url(url, False)
        base64_image = base64.b64encode(img).decode('utf-8')
        return jsonify({'image_base64': base64_image})
    except Exception as e:
        return jsonify({'error': str(e)})
@app.route('/ScrapeStoreStats', methods=['POST'])
def ScrapeStoreStats():
    data = request.json
    domain = data.get('domain')
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--disk-cache-size=1")       
    options.add_argument("--disable-gpu")   
    options.add_argument("--prerender-from-omnibox=disabled")    
    options.add_argument("--disable-software-rasterizer")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.headless = True
    options.add_experimental_option("prefs", prefs)
    windows_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument(f"--user-agent={windows_user_agent}")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options,version_main=122)
    browser.get(f'https://socialblade.com/instagram/user/{domain}')
    browser.implicitly_wait(10)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()
    try:
        statistics_container = soup.find(id="socialblade-user-content").find('div').find_all('div')[3]
    except:
        return jsonify({'stastics':'error in requesting the resource , either your internet connection is slow or you have been blocked by cloudflare'})
    data = []
    json_data = {}
    for stat in statistics_container:
        try:
            raw_data = stat.get_text().strip()
            data.append(raw_data)
        except:
            pass
    try:
        data = list(set(data))
        data.remove('')
        for record in data:
            desc = record.split('\n\n')[1]
            val = record.split('\n\n')[0]
            json_data[desc] = val
        return jsonify(json_data)
    except:
        return jsonify({'stastics':'error in handeling data'})
if __name__ == '__main__':
    app.run(debug=True)
