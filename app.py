import json

import undetected_chromedriver as  webdriver
import re
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
import time
import requests
import pandas as pd
from flask import Flask, request, jsonify
import threading
import queue
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
app = Flask(__name__)

# Queue to handle requests
request_queue = queue.Queue()
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

        options.add_argument(f"--user-agent={windows_user_agent}")
        options.add_argument("--window-size=1920x1080")
        options.add_argument('--load-extension=SimplyTrends')

        browser = webdriver.Chrome(options=options,version_main=118)


        cookies_file = 'cookies_simpletrends.json'
        try:

            browser.get('https://app.simplytrends.co/salestracking/start')

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
            browser.refresh()
            # browser.get('https://app.simplytrends.co/shopifystore/barnerbrand.com')
            browser.get(link)
            domain = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#appBarContainer > div > div > p > p > a.MuiTypography-root.MuiTypography-inherit.MuiLink-root.MuiLink-underlineHover.css-1xa0emq > p')))
            domain_name = domain.text
            dot_position = domain_name.find('.')

            # Extract the text from the dot position to the end of the string
            extension = domain_name[dot_position:] if dot_position != -1 else ''

            print(extension)
            scraped_data['domain_name'] = domain.text
            monthlyunites = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div/div/p')))
            monthlyunites = monthlyunites.text
            print(monthlyunites)
            scraped_data['monthlyunites'] = monthlyunites

            monthlyrevenue = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/p')))
            monthlyrevenue = monthlyrevenue.text
            print(monthlyrevenue)
            scraped_data['monthlyrevenue'] = monthlyrevenue
            country = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(1) > div > div > div > div > p > div > span')))
            country = country.text
            print(country)
            scraped_data['country'] = country
            try:
                countryrank = WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[3]/div/div/div[1]/div[4]/div/div/div/div/p')))
                countryrank = countryrank.text
            except:
                countryrank = "-"
            print(countryrank)
            scraped_data['countryrank'] = countryrank
            try:
                socialmedia = WebDriverWait(browser, 1).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.css-1t62lt9 > span > a')))
                href = socialmedia.get_attribute('href')
            except:
                href = "-"
            print("Extracted URL:", href)
            scraped_data['socialmedia'] = href
            monthstats = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > h2 > span > p > div')))
            monthstats = monthstats.text
            print(monthstats)
            scraped_data['monthstats'] = monthstats
            visible_owerview = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div')))

            print(visible_owerview.text)
            scraped_data['visible_owerview'] = visible_owerview.text
            language = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(2) > div > div > div > div > p')))
            language = language.text
            print(language)
            scraped_data['language'] = language
            currency = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(3) > div > div > div.MuiGrid-root.MuiGrid-container.MuiGrid-item.MuiGrid-grid-xs-12.css-ta72l6 > div:nth-child(3) > div > div > div > div > p')))
            currency = currency.text
            print(currency)
            scraped_data['currency'] = currency
            firstpublishproduct = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > div:nth-child(3) > div:nth-child(1) > div > div > div > div > p')))
            firstpublishproduct = firstpublishproduct.text
            print(firstpublishproduct)
            scraped_data['firstpublishproduct'] = firstpublishproduct
            lastpublishproduct = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > div:nth-child(3) > div:nth-child(2) > div > div > div > div > p')))
            lastpublishproduct = lastpublishproduct.text
            print(lastpublishproduct)
            scraped_data['lastpublishproduct'] = lastpublishproduct
            numproducts = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div:nth-child(4) > div > div:nth-child(3) > div:nth-child(3) > div > div > div > div > p')))
            numproducts = numproducts.text
            print(numproducts)
            scraped_data['numproducts'] = numproducts
            avgprices = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]/div[4]/div/div/div/div/p')))
            avgprices = avgprices.text
            print(avgprices)
            scraped_data['avgprices'] = avgprices
            highestproductprice = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]/div[5]/div/div/div/div/p')))
            highestproductprice = highestproductprice.text
            print(highestproductprice)
            scraped_data['highestproductprice'] = highestproductprice
            lowestproductprice = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]/div[6]/div/div/div/div/p')))
            lowestproductprice = lowestproductprice.text
            print(lowestproductprice)
            scraped_data['lowestproductprice'] = lowestproductprice
            try:
                ch = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[3]/div/div/div/div/div[8]/p'))).click()
                ch = WebDriverWait(browser, 120).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div')))
            except:
                ch = WebDriverWait(browser, 2).until(
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
                click = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/button'))).click()
            except:
                pass

            try:
             click = WebDriverWait(browser, 2).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[6]/div/div/div/div/div/div[8]/p'))).click()
             click = WebDriverWait(browser, 120).until(
                 EC.presence_of_element_located((By.XPATH,
                                                 '/html/body/div[3]/div[3]/div/div/div')))
            except:
                click = WebDriverWait(browser, 120).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[5]/div/div/div')))
                pass

            time.sleep(1)


            div_html = click.get_attribute('innerHTML')

            soup = BeautifulSoup(div_html, 'html.parser')

            # Define a list to hold all the rows of data
            data_producttags = []

            vendor_divs = soup.find_all('div', class_='css-1dogkm')

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





                # Extract the number of products. It's in the next div with class 'css-18jpfvm'
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').get_text(strip=True)
                # num_products = vendor.find_next_sibling('div', class_='css-18jpfvm').find('p').get_text(strip=True)


                # Append the data to the list
                data_producttags.append({'Product_tag': vendor_name, 'Distribution': distribution,
                                         'Number of products': num_products})

            # Create a DataFrame

            df_producttags = pd.DataFrame(data_producttags)

            # Print the DataFrame
            print(df_producttags)
            scraped_data['df_producttags'] = data_producttags
            try:
                click = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/button'))).click()
            except:
                pass
            try:
                click = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]/div[5]/div/div/div/div/div/div[8]/p'))).click()
                click = WebDriverWait(browser, 120).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/div')))
            except:
                click = WebDriverWait(browser, 120).until(
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
                click = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[3]/div[3]/div/div/button'))).click()
            except:
                pass

            click = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/header/div[2]/div[2]/div/div/div/nav/div/div/div/div[1]/button[3]'))).click()
            visible_traffic = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]/div/div/div/div/div/div')))

            print(visible_traffic.text)
            scraped_data['visible_traffic'] = visible_traffic.text
            try:
                monthlyvisits = WebDriverWait(browser, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    '#__next > div > div.app-container-box.MuiBox-root.css-w8kjuh > div > div > div > div > div > div > div > div:nth-child(1) > div > div:nth-child(1) > div > div > div > div > p.MuiTypography-root.MuiTypography-h6.css-1krdksj')))
                monthlyvisits = monthlyvisits.text
                print(monthlyvisits)
                scraped_data['monthlyvisits'] = monthlyvisits

                avgvisitduration = WebDriverWait(browser, 120).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[2]/div/div/div/div/p')))
                avgvisitduration = avgvisitduration.text
                print(avgvisitduration)
                scraped_data['avgvisitduration'] = avgvisitduration

                pagespervisit = WebDriverWait(browser, 120).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[3]/div/div/div/div/p')))
                pagespervisit = pagespervisit.text
                print(pagespervisit)
                scraped_data['pagespervisit'] = pagespervisit

                bouncertate = WebDriverWait(browser, 120).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div[4]/div/div/div/div/p')))
                bouncertate = bouncertate.text
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
                label_name = ''
                percentage = ''
                # Extracting the percentages
                for group in label_groups:
                    text_element = group.find('text')
                    if text_element:
                        percentage = text_element.get_text(strip=True)
                    path_element = group.find_previous_sibling('path')
                    if path_element and 'name' in path_element.attrs:
                        label_name = path_element['name']
                    data_malefepercent.append({label_name: percentage})

                print(data_malefepercent)
                scraped_data['data_malefepercent'] = data_malefepercent
                try:
                    click = WebDriverWait(browser, 2).until(
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
            click = WebDriverWait(browser, 12).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/header/div[2]/div[2]/div/div/div/nav/div/div/div/div[1]/button[4]'))).click()
            time.sleep(1)
            visible_text_tech = WebDriverWait(browser, 120).until(
                EC.presence_of_element_located((By.XPATH,
                                                '/html/body/div[1]/div/div[2]')))

            print(visible_text_tech.text)
            scraped_data['visible_text_tech'] = visible_text_tech.text


            browser.quit()


        except  Exception as e:
            print(a)

            pass





    except:
        print(a)


        browser.quit()
        print('exception')

    result_queue.put(scraped_data)
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
    thread = threading.Thread(target=scraper_function, args=(link, result_queue))
    thread.start()

    # Wait for the result
    result = result_queue.get()

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

