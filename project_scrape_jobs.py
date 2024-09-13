import os
import pandas as pd
import streamlit as st
import textwrap
import random
from IPython.display import Markdown
from groq import Groq
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin  # To handle relative URLs
from connection import Database

import requests
from bs4 import BeautifulSoup
import re
import numpy as np


class ScrapeJobs:
    def __init__(self):
        return
    # Function to scrape job data
    def scrape_upwork_job_data(zenrows_apikey, input_csv='job_links.csv', output_csv='upwork_job.csv'):
        zenrows_base_url = 'https://api.zenrows.com/v1/'

        def zenrows_request(url):
            params = {
                'url': url,
                'apikey': zenrows_apikey,
                'js_render': 'true'
            }
            response = requests.get(zenrows_base_url, params=params)
            
            if 'text/html' in response.headers.get('Content-Type', '') or 'text/plain' in response.headers.get('Content-Type', ''):
                return response
            else:
                return None
            
        def extract_and_format_hourly_rates(soup):
            rates = []
            element = soup.find(attrs={"data-test": "BudgetAmount"})
            if element:
                p_tag = element.find('p')
                if p_tag:
                    strong_tag = p_tag.find('strong')
                    if strong_tag:
                        rates.append(strong_tag.get_text(strip=True))
            
            p_tags = soup.find_all('p')
            for p in p_tags:
                text = p.get_text(strip=True)
                match = re.search(r'\$[0-9]+(?:\.[0-9]{1,2})?', text)
                if match:
                    rates.append(match.group())

            numeric_rates = []
            for rate in rates:
                match = re.search(r'\$([0-9]+(?:\.[0-9]{1,2})?)', rate)
                if match:
                    numeric_rates.append(float(match.group(1)))
            
            if numeric_rates:
                min_rate = min(numeric_rates)
                max_rate = max(numeric_rates)
                return f"${min_rate} - ${max_rate}"
            else:
                return 'N/A'

        def extract_skills(soup):
            skills = set()
            skill_list_count = 0

            relevant_section = soup.find(class_="popover")
            if relevant_section:
                skill_elements = relevant_section.find_all(attrs={"data-test": "Skill"})
                
                for skill_element in skill_elements:
                    if 'skill-list' in skill_element.get('class', []):
                        skill_list_count += 1
                        if skill_list_count > 2:
                            break

                    spans = skill_element.find_all('span')
                    for span in spans:
                        skill_text = span.get_text(strip=True)
                        if skill_text:
                            skills.add(skill_text)

            return ', '.join(skills) if skills else 'N/A'

        df = pd.read_csv(input_csv)

        job_titles = []
        job_descriptions = []
        hourly_rates = []
        required_skills = []
        posted_on_dates = []
        about_clients = []
        clients_histories = []

        for index, row in df.iterrows():
            url = row['Job Link']
            print(url)
            response = zenrows_request(url)

            if response is not None:
                job_soup = BeautifulSoup(response.content, 'html.parser')
                print(job_soup)
                job_title = job_soup.find(class_='m-0')
                job_title_text = job_title.text.strip() if job_title else 'N/A'
                job_titles.append(job_title_text)

                des_element = job_soup.find(attrs={"data-test":"Description"})
                des_p = des_element.find('p') if des_element else None
                des_text = des_p.get_text() if des_p else 'N/A'
                job_descriptions.append(des_text)

                formatted_hourly_rate = extract_and_format_hourly_rates(job_soup)
                hourly_rates.append(formatted_hourly_rate)

                formatted_skills = extract_skills(job_soup)
                required_skills.append(formatted_skills)

                posted_element = job_soup.find(attrs={"data-test":"PostedOn"})
                posted_span = posted_element.find('span') if posted_element else None
                posted_text = posted_span.get_text() if posted_span else 'N/A'
                posted_on_dates.append(posted_text)

                about_client_section = job_soup.find(class_='cfe-about-client-v2')
                about_clients.append(about_client_section.text.strip() if about_client_section else np.nan)

                client_history_section = job_soup.find(class_='cfe-client-history-v2')
                clients_histories.append(client_history_section.text.strip() if client_history_section else np.nan)

        output_df = pd.DataFrame({
            'Job Title': job_titles,
            'Job Description': job_descriptions,
            'Hourly Rate': hourly_rates,
            'Required Skills': required_skills,
            'Posted On': posted_on_dates,
            'About the Client': about_clients,
            'Clients History': clients_histories
        })

        output_df.to_csv(output_csv, index=False)
        # Create an instance of Database and call the insertion method
        db_instance = Database()
        db_instance.insertion_of_data(output_csv)
        
        # Print job titles and index numbers to terminal
        print("Job Index and Titles:")
        for index, title in enumerate(job_titles):
            print(f"{index}: {title}")

        st.success(f"Data saved to {output_csv}")

