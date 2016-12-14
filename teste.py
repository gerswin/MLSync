import sys

sys.path.append('lib')
import math
from meli import Meli
import requests

from woocommerce import API

key = "APP_USR-5747735731654676-081623-cffdb2682030f7cc2dacb273e32d824a__K_E__-154479984"
refresh = "TG-57b0e3dbe4b0cd959edf1069-154479984"


class Melif23:
    def __init__(self, url):
        self.auth = self.get_auth(url)
        self.meli = Meli(client_id=5747735731654676, client_secret="ITYNDyPRzGGArOuwJk2684LwDiGotzCW",
                         access_token=self.auth['access_token'],
                         refresh_token=self.auth['refresh_token'])

    @classmethod
    def get_auth(self, url):
        return requests.get(url, verify=False).json()

    def get_item(self, item):
        response = self.meli.get("/items/" + item).json()
        categories = self.get_categories(response["category_id"])
        return {"id": response["id"], "title": response["title"], "subtitle": response["subtitle"],
                "price": response["price"], "image": response['pictures'][0]['secure_url'], "categories": categories}

    def get_categories(self, cat):
        response = self.meli.get("/categories/" + cat).json()
        return {"main": response["name"], "root": response["path_from_root"], "childs": response["children_categories"]}

    def get_user(self):
        params = {'access_token': self.meli.access_token}
        response = self.meli.get(path="/users/me", params=params).json()
        return response["id"]


class Wooadd(Melif23):
    def __init__(self, url):
        Melif23.__init__(self, url)
        self.wcapi = API(
            url="https://full23.com",
            consumer_key="ck_6f0629136b2ced84eedac59bd698b85b85bbb08b",
            consumer_secret="cs_fb2db037cea70be81fd3ab1c65ff6be90a18960e",
            wp_api=True,
            version="wc/v1",
            verify_ssl=False
        )

    def add_categories(self, category, parent=None):
        data = {
            "name": category,
            "parent": parent
        }
        # try:
        resp = self.wcapi.post("products/categories", data).json()
        try:
            return resp['id']
        except KeyError:
            return resp['data']
        except:
            pass

    def add_main_categories(self, category):
        return self.add_categories(category)

    def add_root_categories(self, categories):
        old_cat = None
        for cat in categories:
            r = self.add_categories(cat['name'], old_cat)
            old_cat = str(r)

        return old_cat

    def clean_store(self):
        while len(self.wcapi.get("products").json()) > 0:
            items = self.wcapi.get("products").json()
            for i in items:
                self.delete_item(i['id'])

    def delete_item(self, item):
        self.wcapi.delete("products/" + str(item) + "?force=true")

    def add_item(self, item):
        producto = self.get_item(item)
        cat_id = self.add_root_categories(producto['categories']['root'])
        data = {
            "name": producto['title'],
            "type": "simple",
            "regular_price": str(producto['price']),
            "description": "",
            "short_description": "",
            "categories": [
                {
                    "id": cat_id
                }

            ],
            "images": [
                {
                    "src": producto['image'],
                    "position": 0
                }
            ]
        }
        return (self.wcapi.post("products", data).json())


full23 = Wooadd("https://full23.com/core/api/index.php/a3wfnrg2x4kr929c")

a = full23.clean_store()

# full23.add_item("MLV466061309")
userid = full23.get_user()
items = []
mel = Meli(client_id=5747735731654676, client_secret="ITYNDyPRzGGArOuwJk2684LwDiGotzCW", access_token=key,
           refresh_token=refresh)
params = {'access_token': key, "limit": 50}
resp = mel.get("/users/" + str(userid) + "/items/search", params=params).json()
for i in resp['results']:
    items.append(i)

times = math.ceil(int(resp['paging']['total']) / 50) + 1
offset = 0

for i in range(0, int(times)):
    params = {'access_token': key, "limit": 50, "offset": offset}
    resp = mel.get("/users/" + str(userid) + "/items/search", params=params).json()
    for i in resp['results']:
        items.append(i)

    offset = offset + 50

for i in items:
    full23.add_item(i)
