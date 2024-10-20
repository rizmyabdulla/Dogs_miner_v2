from fake_useragent import UserAgent

ua = UserAgent()

def get_headers(cookie, csrf):
    """Returns headers with the specified session cookie and random user-agent."""
    return {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'cookie': cookie,
        'priority': 'u=1, i',
        'referer': 'https://dogs.triplecloudmining.com/',
        'sec-ch-ua': f'"{ua.random}"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': ua.random,
        'x-csrf-token': csrf,
        'x-requested-with': 'XMLHttpRequest'
    }
