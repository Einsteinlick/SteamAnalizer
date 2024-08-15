import re
import requests
from bs4 import BeautifulSoup
import time
import random
from Proxies import proxies


def get_dota2_market_items(hero_name, page):
    url = f'https://steamcommunity.com/market/search?q=&category_570_Hero[]=tag_npc_dota_hero_{hero_name}&category_570_Slot[]=any&category_570_Type[]=any&category_570_Quality[]=tag_unique&appid=570#p{page}_price_desc'

    for _ in range(len(proxies)):
        proxy = random.choice(proxies)
        try:
            response = requests.get(url, proxies=proxy, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all(class_='market_listing_row_link')
            results = []

            for item in items:
                name = item.find(class_='market_listing_item_name').text.strip()
                href = item.get('href', '')
                price_tag = item.find(class_='normal_price')
                price_value = None

                if price_tag:
                    price_text = price_tag.text.strip()
                    match = re.search(r'[\d\.]+', price_text)
                    if match:
                        price_value = float(match.group())

                results.append({
                    'name': name,
                    'href': href,
                    'price': price_value
                })

            right_results = []
            for item in results:
                href = item['href']
                parts = href.split('/')
                parts[6] = 'Inscribed%20' + parts[6]
                corrected_href = '/'.join(parts)

                response = requests.get(corrected_href, proxies=proxy, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                with_fee_elements = soup.find_all('span', class_='market_listing_price market_listing_price_with_fee')
                dollar_value = None

                for element in with_fee_elements:
                    with_fee_text = element.text.strip()
                    dollar_match = re.search(r'\$([\d.,]+)\sUSD', with_fee_text)
                    if dollar_match:
                        dollar_value = float(dollar_match.group(1))

                if dollar_value is not None and (item['price'] + 0.08) * 1.15 < dollar_value:
                    dev = dollar_value - item['price']
                    item['profit'] = dev
                    right_results.append(item)

            time.sleep(random.uniform(2, 3))
            return right_results

        except requests.RequestException as e:
            print(f"Request failed with proxy {proxy}. Error: {e}")
            continue

    return []
