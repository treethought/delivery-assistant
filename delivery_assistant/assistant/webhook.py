import os
import logging
from typing import Dict, List
from flask import Blueprint
from flask_assistant import Assistant, ask, tell, build_item
from delivery_assistant.utilities.scraper import OrderScraper


blueprint = Blueprint('assist', __name__, url_prefix='/assist')
assist = Assistant(blueprint=blueprint)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

##################################################
USERNAME = os.getenv('MC_USERNAME')
PASSWORD = os.getenv('MC_PASSWORD')
d = OrderScraper(USERNAME, PASSWORD)

def map_url(address):
    query = address.replace(' ', '+')
    return 'https://www.google.com/maps/place/{}'.format(query)

def get_order_items(order: Dict[str, str]) -> List[Dict[str, str]]:
    items = []
    for k, v in order.items():
        i = build_item(title=k, key=k, description=v)
        items.append(i)
    return items


@assist.action('Greetings')
def welcome():
    speech = 'Hey! Im the delivery assistant. Try Asking me for the leatest order.'
    return ask(speech).suggest('Latest Order', 'Shift OverView')

@assist.action('LatestOrder')
def get_latest():
    data = d.latest
    if data is None:
        return tell('You dont have any orders yet!')

    speech = "Your current order is from {} at {}".format(data['Restaurant'], data['Pickup Time'])
    order_items = get_order_items(data)
    resp = tell(speech).build_list()
    resp.include_items(order_items)

    order_url = d.get_order_url(data['OrderId'])  # maybe move into scraper
    resp.link_out('View Order', order_url)      # and add to the order dict

    return resp

@assist.action('ViewOrder')
def view_order_details(order_id):
    speech = 'Message'
    return ask(speech)


if __name__ == '__main__':
    app.run(debug=True)



