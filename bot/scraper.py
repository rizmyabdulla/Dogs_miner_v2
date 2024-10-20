import requests
from bs4 import BeautifulSoup
from headers import get_headers

def fetch_user_data(cookie, csrf_token):
    """ Fetch user data from the site and return the user details. """
    url = "https://dogs-miner.triplecloudmining.com"
    response = requests.get(url, headers=get_headers(cookie, csrf_token))
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        user_info = soup.find('div', id='user_info_render')
        user_name = user_info.find('h2').get_text(strip=True)
        user_id = user_info.find('input', id='user_id')['value']
        ads_count = soup.find('div', id='countdownDisplay')
        balance_section = soup.find('div', class_='balance')
        balance_text = balance_section.find('p').get_text(strip=True)
        balance_amount = balance_text.split()[0]
        remaining_ads = ads_count.get_text(strip=True)
        watched_ads, max_ads = map(int, remaining_ads.split(' / '))
        
        return {
            "user_name": user_name,
            "user_id": user_id,
            "balance_amount": balance_amount,
            "watched_ads": watched_ads,
            "max_ads": max_ads
        }
    else:
        print(f"Failed to retrieve page, status code: {response.status_code}")
        return None