import requests
from bs4 import BeautifulSoup
import os
import logging
import json
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def scrape_apollo():
    url = "https://app.apollointeligence.com/login/"
    email = os.environ.get('APOLLO_EMAIL', 'jmccabeVA@gmail.com')
    password = os.environ.get('APOLLO_PASSWORD', 'moon;MARS;musk1')

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': url
    }

    try:
        # Step 1: Login
        logger.info("Fetching login page...")
        res = session.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        form = soup.find('form')
        login_data = {}
        for input_tag in form.find_all('input'):
            name = input_tag.get('name')
            if name:
                login_data[name] = input_tag.get('value', '')

        email_field = None
        password_field = None
        for name in login_data.keys():
            if 'email' in name.lower() or 'username' in name.lower() or 'login' in name.lower():
                email_field = name
            elif 'pass' in name.lower():
                password_field = name
                
        login_data[email_field or 'email'] = email
        login_data[password_field or 'password'] = password

        post_url = url
        if form.get('action'):
            from urllib.parse import urljoin
            post_url = urljoin(url, form.get('action'))
            
        res_post = session.post(post_url, data=login_data, headers=headers, allow_redirects=True)
        
        if "Logout" not in res_post.text and "Dashboard" not in res_post.text:
            logger.error("Login failed. Check credentials.")
            return

        logger.info("Login successful. Hitting prediction API...")

        # Step 2: Trigger Scraping Task for Powerball
        csrf_token = session.cookies.get("csrftoken") or login_data.get('csrfmiddlewaretoken')
        api_headers = headers.copy()
        api_headers.update({
            "X-CSRFToken": csrf_token,
            "Referer": "https://app.apollointeligence.com/",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        })

        game_key = "virginia_powerball"
        start_res = session.post(f"https://app.apollointeligence.com/start_scrape_task/{game_key}/", headers=api_headers, json={})
        logger.info(f"Start Task Response: {start_res.status_code} - {start_res.text}")

        # Step 3: Poll for results
        for _ in range(15):
            time.sleep(2)
            poll_res = session.get(f"https://app.apollointeligence.com/get_scrape_result/{game_key}/", headers=api_headers)
            result = poll_res.json()
            logger.info(f"Poll Result: {result}")
            if result.get("status") != "PENDING":
                break

    except Exception as e:
        logger.error(f"Exception during login test: {e}")

if __name__ == '__main__':
    scrape_apollo()