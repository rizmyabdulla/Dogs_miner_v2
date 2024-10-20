import asyncio
import aiohttp
import ssl
import json
import argparse
from fake_useragent import UserAgent
from colorama import init, Fore, Style
from pathlib import Path
from scraper import fetch_user_data
from headers import get_headers

init(autoreset=True)

ua = UserAgent()

daily_url = 'https://dogs-miner.triplecloudmining.com/get/advertisement/reward'

SESSION_FILE = 'sessions.json'
PROXY_FILE = 'proxies.json'


class Tapper:
    def __init__(self, session_name, cookie, csrf_token, proxy=None):
        self.session_name = session_name
        self.cookie = cookie
        self.csrf_token = csrf_token
        self.proxy = proxy
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def fetch_user_info_periodically(self):
        """ Fetch user info and print every 15 seconds. """
        while True:
            user_data = fetch_user_data(self.cookie, self.csrf_token)
            if user_data:
                print(Fore.CYAN + f"[{self.session_name}] User: {user_data['user_name']}, ID: {user_data['user_id']}, Balance: {user_data['balance_amount']} Dogs, Remaining Ads: {user_data['max_ads'] - user_data['watched_ads']}")
            else:
                print(Fore.RED + f"[{self.session_name}] Failed to fetch user data")
            await asyncio.sleep(15)

    async def daily_ad(self, session):
        """ Claims the daily advertisement reward asynchronously, counting the remaining ads. """

        while True:
            user_data = fetch_user_data(self.cookie, self.csrf_token)  
            watched_ads = user_data['watched_ads']
            max_ads = user_data['max_ads']

            if watched_ads == max_ads:
                print(Fore.GREEN + f"[{self.session_name}] No more ads left to claim today!")
                break

            try:
                async with session.get(daily_url, headers=get_headers(self.cookie, self.csrf_token), proxy=self.proxy, ssl=self.ssl_context) as response:
                    if response.status == 200:
                        print(Fore.CYAN + f"[{self.session_name}] Claimed daily reward {watched_ads}/{max_ads}! Got 0.25 Dogs!")
                    else:
                        print(Fore.RED + f"[{self.session_name}] Failed to claim daily reward. Status code: {response.status}")

            except aiohttp.ClientError as e:
                print(Fore.RED + f"[{self.session_name}] Error claiming daily reward: {e}")
            
            await asyncio.sleep(1.5)

        print(Fore.GREEN + f"[{self.session_name}] Finished claiming daily rewards!")

async def run_session(session_name, cookie, csrf_token, proxy=None):
    """ Runs both daily_ad and fetch_user_info_periodically functions for a specific session """
    tapper = Tapper(session_name, cookie, csrf_token, proxy)
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            tapper.fetch_user_info_periodically(),
            tapper.daily_ad(session)
        )

def load_sessions():
    """ Load session data from a JSON file """
    if not Path(SESSION_FILE).is_file():
        return {}

    try:
        with open(SESSION_FILE, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(Fore.RED + f"Error loading sessions: {e}")
        return {}



def load_proxies():
    """ Load proxy data from a JSON file """
    if not Path(PROXY_FILE).is_file():
        return {}

    with open(PROXY_FILE, 'r') as file:
        return json.load(file)


def save_sessions(sessions):
    """ Save session data to a JSON file """
    with open(SESSION_FILE, 'w') as file:
        json.dump(sessions, file, indent=4)


def add_session():
    """ Add a new session interactively and save it to the JSON file """
    session_name = input(Fore.CYAN + "Enter the session name: ").strip()
    cookie = input(Fore.CYAN + "Enter the session cookie: ").strip()
    csrf_token = input(Fore.CYAN + "Enter the CSRF token: ").strip()

    if session_name and cookie and csrf_token:
        sessions = load_sessions()
        sessions[session_name] = {
            "cookie": cookie,
            "csrf_token": csrf_token
        }
        save_sessions(sessions)
        print(Fore.GREEN + f"Session '{session_name}' added successfully!")
    else:
        print(Fore.RED + "Session name, cookie and CSRF token cannot be empty!")


def add_proxy():
    """ Add a proxy interactively and save it to the proxies JSON file """
    proxy_name = input(Fore.CYAN + "Enter the proxy name: ").strip()
    proxy_url = input(Fore.CYAN + "Enter the proxy URL (format: http://user:password@proxyserver:port or http://proxyserver:port): ").strip()

    if proxy_name and proxy_url:
        proxies = load_proxies()
        proxies[proxy_name] = proxy_url
        with open(PROXY_FILE, 'w') as file:
            json.dump(proxies, file, indent=4)
        print(Fore.GREEN + f"Proxy '{proxy_name}' added successfully!")
    else:
        print(Fore.RED + "Proxy name and URL cannot be empty!")


async def main(selected_sessions, use_proxy):
    """ Main function to run selected sessions asynchronously """
    print(Fore.CYAN + "Loading sessions...")
    sessions = load_sessions()
    proxies = load_proxies() if use_proxy else {}

    if not sessions:
        print(Fore.YELLOW + "No sessions found. Please add one first.")
        add_session()

    tasks = []
    for session_name, session_data in sessions.items():
        if not selected_sessions or session_name in selected_sessions:
            proxy = proxies.get(session_name) if use_proxy else None
            tasks.append(run_session(session_name, session_data['cookie'], session_data['csrf_token'], proxy))


    if tasks:
        print(Fore.GREEN + f"Running {len(tasks)} session(s) concurrently.")
        await asyncio.gather(*tasks)
    else:
        print(Fore.RED + "No valid sessions to run.")


def interactive_menu():
    """ command-line interface for managing sessions and proxies """

    print(Fore.MAGENTA + "Welcome to the Dogs Miner Script!")
    print("\n")
    print(Fore.MAGENTA + "Created by: https://t.me/NotMrStrange")
    print(Fore.MAGENTA + "Join our Tg group: https://t.me/yk_daemon")
    print(Fore.MAGENTA + "Youtube: https://www.youtube.com/@Yk-Daemon")
    print("\n")
    print(Fore.CYAN + "What would you like to do?")
    while True:
        print("\n")
        print("1. Add a new session")
        print("2. Add a proxy")
        print("3. Run all sessions")
        print("4. Run specific sessions")
        print("5. Exit")
        print("\n")
        
        choice = input(Fore.YELLOW + "Choose an option: ").strip()

        if choice == "1":
            add_session()
        elif choice == "2":
            add_proxy()
        elif choice == "3":
            asyncio.run(main([], use_proxy=False))
        elif choice == "4":
            selected_sessions = input(Fore.CYAN + "Enter session names (comma separated): ").split(',')
            asyncio.run(main([session.strip() for session in selected_sessions], use_proxy=False))
        elif choice == "5":
            print(Fore.GREEN + "Exiting... See you :)")
            break
        else:
            print(Fore.RED + "Invalid choice! Please try again.")


def parse_arguments():
    """ Parse command-line arguments """
    parser = argparse.ArgumentParser(description="Run Dogs Tapper sessions asynchronously.")
    parser.add_argument('-r', '--run', nargs='*', help="Run specific session(s) by name")
    parser.add_argument('-a', '--add', action='store_true', help="Add a new session")
    parser.add_argument('-p', '--proxy', action='store_true', help="Enable proxy support")
    parser.add_argument('--add-proxy', action='store_true', help="Add a new proxy")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    if args.add:
        add_session()

    elif args.add_proxy:
        add_proxy()

    elif args.run:
        try:
            asyncio.run(main(args.run, args.proxy))
        except KeyboardInterrupt:
            print(Fore.GREEN + "\nSee you 👋")

    else:
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print(Fore.GREEN + "\nSee you 👋")