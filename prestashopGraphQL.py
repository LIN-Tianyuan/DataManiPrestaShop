"""
@Time ：02/04/2024 14:54
@Auth ：LIN Tianyuan
@File ：prestashopGraphQL.py
@Motto：ABC(Always Be Coding)
"""

import requests
from enum import Enum
import datetime
from datetime import datetime, date
import xml.etree.ElementTree as ET


class LangageType(Enum):
    ENGLISH_NAME = 1
    FRENCH_NAME = 2

class PrestashopGraphQLException(Exception):
    pass


class PrestashopGraphQLNoImageException(Exception):
    pass


class PrestashopGraphQL:
    def __init__(self, shop_url, api_key):
        self.shop_url = shop_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def _request_graphql2(self, query):
        # /api/categories&display=full?output_format=JSON&filter[id]=2
        resource = query['resource']
        if query['fil']:
            print(query['fil'].keys())
    def _request_graphql(self, query):
        # /api/categories&display=full?output_format=JSON&filter[id]=2
        resource = query['resource']
        if query['fil']:
            if 'id' in query['fil'].keys():
                url = f"{self.shop_url}/api/{resource}&display=full?output_format=JSON&filter[id]={query['fil']['id']}"
            elif 'email' in query['fil'].keys():
                url = f"{self.shop_url}/api/{resource}&display=full?output_format=JSON&filter[email]={query['fil']['email']}"
            elif 'id_customer' in query['fil'].keys():
                url = f"{self.shop_url}/api/{resource}&display=full?output_format=JSON&filter[id_customer]={query['fil']['id_customer']}"
        else:
            url = f"{self.shop_url}/api/{resource}&display=full?output_format=JSON"


        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        raise PrestashopGraphQLException("Bad API response (object format)")

    def _request_graphql_xml(self, query):
        resource = query['resource']
        if "products" in resource:
            url = f"{self.shop_url}/api/{resource}&display=full"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 404:
            return None
        else:
            raise PrestashopGraphQLNoImageException("Bad API response (object format)")



    @staticmethod
    def get_need_language(attr, l_type):
        check_name = ""
        if l_type == LangageType.ENGLISH_NAME:
            check_name = attr[0]['value']
        elif l_type == LangageType.FRENCH_NAME:
            check_name = attr[1]['value']
        return check_name

    @staticmethod
    def get_product_image(self, product_id):
        image_infos = []
        query1 = {"resource": f"images/products/{product_id}", "fil": ""}
        res_product = self._request_graphql_xml(query1)
        if res_product:
            root = ET.fromstring(res_product)
            namespaces = {'xlink': 'http://www.w3.org/1999/xlink'}

            for elem in root.findall('.//*[@xlink:href]', namespaces):
                href_value = elem.get('{http://www.w3.org/1999/xlink}href')
                image_infos.append(href_value)
            return image_infos[0]
        else:
            return "No image"

    def get_pon_by_pov(self, pov_id):
        query3 = {"resource": "product_options", "fil": ""}
        res_product_option = self._request_graphql(query3)
        product_options = res_product_option['product_options']
        for product_option in product_options:
            option_id_list = []
            option_ids= product_option['associations']['product_option_values']
            for option_id in option_ids:
                option_id_list.append(option_id['id'])
            if pov_id in option_id_list:
                return self.get_need_language(product_option['name'], LangageType.ENGLISH_NAME)

    def get_days(self, start_date):
        """
        Get the time difference between two dates
        :param start_date:
        :return:
        """
        d1 = datetime.strptime(str(date.today()), '%Y-%m-%d')
        d2 = datetime.strptime(start_date.split(' ')[0], '%Y-%m-%d')
        return (d1 - d2).days

    def get_category_type(self, cat_id, l_type):
        query = {"resource": "categories", "fil": {}}
        query["fil"]['id'] = int(cat_id)
        res_category = self._request_graphql(query)
        name = res_category['categories'][0]['name']
        check_name = self.get_need_language(name, l_type)
        return check_name

    def get_shop_name(self):
        shop_names = []
        query = {"resource": "shops", "fil": ""}
        res_shop = self._request_graphql(query)
        try:
            for shop in res_shop['shops']:
                shop_names.append(shop['name'])
        except:
            raise PrestashopGraphQLException("Bad API response (object format)")
        return shop_names

    def get_shop_info(self):
        shop_infos = {}
        query = {"resource": "shops", "fil": ""}
        res_shop = self._request_graphql(query)
        try:
            for shop in res_shop['shops']:
                shop_infos['name'] = shop['name']
                query["resource"] = "categories"
                query["fil"] = {}
                query["fil"]['id'] = shop['id_category']
                res_category = self._request_graphql(query)
                name = res_category['categories'][0]['name']
                shop_infos['category'] = {}
                english_name = name[0]['value']
                french_name = name[1]['value']
                shop_infos['category']['english_name'] = english_name
                shop_infos['category']['french_name'] = french_name
                return shop_infos
        except:
            raise PrestashopGraphQLException('Bad API response (object format)')

    def get_product_categories(self):
        categories_names = {'english_name': [], 'french_name': []}
        query = {"resource": "categories", "fil": ""}
        res_cat = self._request_graphql(query)
        try:
            for category in res_cat['categories']:
                english_name = category['name'][0]['value']
                french_name = category['name'][1]['value']
                categories_names['english_name'].append(english_name)
                categories_names['french_name'].append(french_name)
            return categories_names
        except:
            raise PrestashopGraphQLException('Bad API response (object format)')

    def get_all_products(self):
        """id, productType,description,title,onlineStoreUrl"""
        product_infos = []
        query1 = {"resource": "products", "fil": ""}
        res_product = self._request_graphql(query1)
        # print(res_product)
        # query2 = {"resource": "images/products", "fil": ""}
        # image_url = self._request_graphql(query2)
        # print(image_url)
        self.get_product_image(self, 15)
        try:
            for product in res_product['products']:
                english_des = self.get_need_language(product['description'], LangageType.ENGLISH_NAME)
                english_title = self.get_need_language(product['name'], LangageType.ENGLISH_NAME)
                image_url = self.get_product_image(self, product['id'])
                # http://localhost:8888/localinstallation/api/images/products/2/21
                # {{webservice_url}}/api/images/products/2
                # print(product['id'])
                # self.get_product_image(self, 15)
                product_info = {
                    "id": product['id'],
                    "productType": product['product_type'],
                    "description": english_des,
                    "title": english_title,
                    # "onlineStoreUrl":
                    "imageUrl": image_url,
                    "price": product['price'],
                    "publishAt": product['date_add'],
                    "Available": "No" if product['available_for_order'] == '0' else "Yes",
                    "minPrice": product['price'],
                    "maxPrice": product['price']
                }
                product_infos.append(product_info)
            return product_infos

        except:
            raise PrestashopGraphQLException('Bad API response (object format)')

    def get_product_options(self, product_id):
        product_variants = []
        query1 = {"resource": "products", "fil": {"id": product_id}}
        res_product = self._request_graphql(query1)
        product_available = res_product['products'][0]['available_for_order']
        product_option = res_product['products'][0]['associations']['product_option_values']
        selected_options = []
        for product_option_id_dict in product_option:
            product_option_id = product_option_id_dict['id']
            query2 = {"resource": "product_option_values", "fil": {"id": product_option_id}}
            res_product_option = self._request_graphql(query2)
            product_option_value_id = product_option_id_dict['id']
            print(product_option_value_id)
            product_option_name = self.get_pon_by_pov(product_option_value_id)
            print(product_option_name)
            product_option_value = res_product_option['product_option_values'][0]['name']
            eng_product_option_value = self.get_need_language(product_option_value, LangageType.ENGLISH_NAME)
            selected_option = {
                "name": product_option_name,
                "value": eng_product_option_value
            }
            selected_options.append(selected_option)
        product_variants = {
            "availableForSale": "No" if product_available == '0' else "Yes",
            "selectedOptions": selected_options
        }
        return product_variants

    def get_client_information(self, email):
        query1 = {"resource": "customers", "fil": {}}
        query1["fil"]["email"] = email
        res_cat = self._request_graphql(query1)
        cat_info = res_cat['customers'][0]
        query2 = {"resource": "orders", "fil": {"id_customer":cat_info['id']}}
        res_order = self._request_graphql(query2)
        order_info = res_order['orders']
        customer_infos = {
            "id": cat_info['id'],
            "firstname": cat_info['firstname'],
            "lastname": cat_info['lastname'],
            "createdAt": cat_info['date_add'],
            "lifetimeDuration": self.get_days(cat_info['date_add']),
            "numberOfOrders": len(order_info),
            "lastOrder": {
                # "name":
            }
        }
        return customer_infos


if __name__ == "__main__":
    shop_url = "http://localhost:8888/localinstallation"
    api_key = "3XMLLL1F19UEIYC44X8LZTTQCKZZ6W33"

    api = PrestashopGraphQL(shop_url, api_key)

    # shop_name = api.get_shop_name()
    # print(f"Shop name: {shop_name}")
    #
    # shop_info = api.get_shop_info()
    # print(f"Shop info: {shop_info}")
    #
    # categories = api.get_product_categories()
    # print(f"Categories: {categories}")

    # products = api.get_all_products()
    # for product in products:
    #     print(product)

    # client_information = api.get_client_information("pub@prestashop.com")
    # print(client_information)
    options = api.get_product_options(1)
    print(options)

