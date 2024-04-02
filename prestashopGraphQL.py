"""
@Time ：02/04/2024 14:54
@Auth ：LIN Tianyuan
@File ：prestashopGraphQL.py
@Motto：ABC(Always Be Coding)
"""
import requests
import xml.etree.ElementTree as ET


class PrestashopGraphQLException(Exception):
    pass


class PrestashopGraphQL:
    def __init__(self, shop_url, api_key):
        self.shop_url = shop_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def _request_graphql(self, resource):
        url = f"{self.shop_url}/api/{resource}&display=full"
        response = self.session.get(url)
        if response.status_code == 200:
            return self.parse_xml(self, response.content)
        raise PrestashopGraphQLException

    # def get_products(self):
    #     url = f"{shop_url}/api/products"
    #     response = self.session.get(url)
    #     if response.status_code == 200:
    #         return self.get_products_from_xml(response.content)
    #         # return response.content
    #     else:
    #         response.raise_for_status()
    @staticmethod
    def parse_xml(self, xml_data):
        root = ET.fromstring(xml_data)
        return root

    # def get_shop_name(self):
    #     url = f"{shop_url}/api/shops&display=full"
    #     response = self.session.get(url)
    #     return self.get_products_from_xml(response.content)
    def get_shop_name(self):
        response = self._request_graphql('shops')
        try:
            for shop in response.findall('.//shop'):
                shop_name = shop.find('name').text
                return shop_name
        except:
            raise PrestashopGraphQLException('Bad API response (object format)')


    # def get_shop_info(self):
    #     url = f"{shop_url}/api/contacts&display=full"
    #     response = self.session.get(url)
    #     try:
    #         root = self.parse_xml(response.content)
    #         for contact in root.findall('.//contact'):
    #             email = contact.find('email').text
    #             return email
    #         return self.get_products_from_xml(response.content)
    #     except:
    #         raise PrestashopGraphQLException('Bad API response (object format)')
    def get_shop_info(self):
        response = self._request_graphql('contacts')
        try:
            for contact in response.findall('.//contact'):
                email = contact.find('email').text
                return email
        except:
            raise PrestashopGraphQLException('Bad API response (object format)')


    def get_product_categories(self):
        response = self._request_graphql('categories')
        categories_names = []
        try:
            for category in response.findall('.//categories'):
                # for name in category.findall('name'):
                #     category_name = name.find('language').text
                #     categories_names.append(category_name)
                name = category.find('name')


                return categories_names
        except:
            raise PrestashopGraphQLException('Bad API response (object format)')

if __name__ == "__main__":
    shop_url = "http://localhost:8888/localinstallation"
    api_key = "3XMLLL1F19UEIYC44X8LZTTQCKZZ6W33"

    api = PrestashopGraphQL(shop_url, api_key)

    shop_name = api.get_shop_name()
    print(f"Shop name: {shop_name}")

    shop_info = api.get_shop_info()
    print(f"Shop info:\n "
          f"contact email:{shop_info}")

    categories = api.get_product_categories()
    print(categories)
