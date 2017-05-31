
# ORDER SCRAPING ##
from bs4 import BeautifulSoup as bs
import requests

from pprint import pprint

from typing import List, Dict, Any
from bs4.element import Tag


class OrderScraper(object):
    """docstring for OrderScraper"""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._order_base = 'http://d.mealclub.com/order.php?id=' 
        self.login_url = 'http://d.mealclub.com/login.php'
        self._orders = []

    @property
    def login_data(self):
        return {'username': self.username, 'password': self.password}

    @property
    def deliveries(self) -> List[Dict[str, str]]:
        """Delivery Overview from the main page. Used for order status"""
        forms = self._get_delivery_forms()
        deliveries = []
        for form in forms:
            deliveries.append(self._parse_delivery_info(form))
        return deliveries

    @property
    def latest(self) -> Dict[str, str]:
        try:
            return self.orders[0]
        except IndexError:
            return None

    @property
    def order_ids(self):
        ids = []
        for i in self._main_soup.select('tr.order > td > strong'):
            order_id, method = i.get_text().strip().split(' - ')
            ids.append(order_id)
        return ids

    @property
    def orders(self):
        """Returns order dictionaries containing all order info"""
        return [self._parse_order_info(i) for i in self.order_ids]
    
    
    @property
    def unconfirmed(self):
        """New deliveries that haven't been confirmed (Blue)"""
        return [i for i in self.deliveries if i['Status'] == 'Unconfirmed']

    @property
    def confirmed(self):
        """deliveries that have been confirmed and not picked up (Red)"""
        return [i for i in self.deliveries if i['Status'] == 'Confirmed']

    @property
    def picked_up(self):
        return [i for i in self.deliveries if i['Status'] == 'Picked Up']
    

    @property
    def delivered(self):
        """deliveries that have been successfully delivered (Green)"""
        return [i for i in self.deliveries if i['Status'] == 'Delivered']

    def _get_soup(self, url: str) -> bs:
        # login
        resp = self.session.post(self.login_url, self.login_data)
        resp.raise_for_status()
        # go to roder page
        resp = self.session.get(url)
        resp.raise_for_status()
        resp.encoding = 'UTF-8'
        return bs(resp.text, 'html.parser')

    @property
    def _main_soup(self) -> bs:
        resp = self.session.post(self.login_url, self.login_data)
        resp.raise_for_status()
        return bs(resp.text, 'html.parser')

    def _get_delivery_forms(self) -> List[Tag]:
        """Returns the submission forms from the main delivery list page"""
        soup = self._main_soup()
        return soup.find_all('form')

    def _get_order_soup(self, order_id: str) -> List[Tag]:
        """Returns the tables from the order's detail page"""
        url = self._order_base + order_id
        soup = self._get_soup(url)
        return soup


    def _parse_delivery_info(self, delivery_form: Tag) -> Dict[str, str]:
        data = {}
        for row in delivery_form.select('tr'):
            field, value = row.find('th'), row.find('td')
            if value is not None and field is not None:
                f = field.get_text().replace(u'\xa0', ' ').strip().strip(':')
                v = value.get_text().replace(u'\xa0', ' ').strip()
                data[f] = v
        data.pop('Time Delivered', None) # Time delivered is just a drop down list for times
        return data

    def _parse_dish_info(self, dish_table: Tag) -> Dict[str, str]:
        data = {}
        data['dishes'] = []
        for row in dish_table.select('tr'):
            tds = row.find_all('td')
            
            if len(tds) == 3: # dish item
                dish_name = tds[1].get_text().replace(' ', '').replace('\n', '').strip('\t')
                dish_price = tds[2].get_text()
                data['dishes'].append({dish_name: dish_price})

            elif len(tds) == 2:  # charges
                f = tds[0].get_text().replace(u'\xa0', ' ').strip().strip(':')
                v = tds[1].get_text().replace(u'\xa0', ' ').strip().strip(':')
                data[f] = v
        return data




    def _parse_order_info(self, order_id: str) -> Dict[str, str]:
        order_info = {}

        soup = self._get_order_soup(order_id)
        overview = soup.select('#content > p')[0].get_text()
        order_info['Restaurant'] = overview.split(' - ')[1]



        tables = soup.find_all('table')


        order_info.update(self._parse_delivery_info(tables[0]))  # Order info table : same th, td format as on main page
        dish_data = self._parse_dish_info(tables[1])
        order_info.update(dish_data)
        return order_info

