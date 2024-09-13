import streamlit as st
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin  # To handle relative URLs

class Scraping_Links:
    def __init__(self):
        return

    # Function to scrape job links
    def scrape_job_links(domain, output_csv='job_links.csv'):
        chrome_driver_path = r'C:/Users/Fasih Arif/Downloads/chromedriver-win64/chromedriver.exe'
        brave_binary_path = r'C:/Program Files/Google/Chrome/Application/chrome.exe'
        chrome_options = Options()
        chrome_options.binary_location = brave_binary_path
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        domain_formatted = domain.replace(" ", "%20")
        url = f"https://www.upwork.com/nx/search/jobs/?q={domain_formatted}&page=1&per_page=10"
        
        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        driver.get(url)

        try:
            job_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.up-n-link'))
            )
            
            job_links = set()
            for element in job_elements:
                href = element.get_attribute('href')
                if href and '/jobs/' in href:
                    href = urljoin(url, href)
                    job_links.add(href)
            
            with open(output_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Job Link'])
                for link in job_links:
                    writer.writerow([link])
            
            st.success(f"Saved {len(job_links)} job links to {output_csv}")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        finally:
            driver.quit()

