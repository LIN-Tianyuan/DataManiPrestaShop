"""
@Time ：02/04/2024 14:54
@Auth ：LIN Tianyuan
@File ：prestashopREST.py
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


class PrestashopRESTException(Exception):
    pass


class PrestashopRESTConnectException(PrestashopRESTException):
    pass


class PrestashopRESTBadRequestException(PrestashopRESTException):
    pass


class PrestashopRESTInvalidTokenException(PrestashopRESTException):
    pass


class PrestashopRESTNoImageException(PrestashopRESTException):
    pass


class PrestashopRESTURLNotFoundException(PrestashopRESTException):
    pass


class PrestashopRESTQueryErrorsException(PrestashopRESTException):
    pass


class PrestashopREST:

    _REQUIRED_APP_ACCESS_SCOPES = [
        'Addresses', 'Attachments', 'Carriers', 'Cart rules', 'Carts', 'Categories', 'Combinations',
        'Configurations', 'Contacts', 'Content management system', 'Countries', 'Currencies', 'Customer messages',
        'Customer threads', 'Customers', 'Customizations', 'Deliveries', 'Employees', 'Groups', 'Guests',
        'Image types', 'Images', 'Languages', 'Manufacturers', 'Messages', 'Order carriers',
        'Order cart rules', 'Order details', 'Order histories', 'Order invoices', 'Order payments',
        'Order slip', 'Order states', 'Orders', 'Price ranges', 'Product customization fields',
        'Product feature values', 'Product features', 'Product option values', 'Product options',
        'Product suppliers', 'Products', 'Search', 'Shop groups', 'Shop urls', 'Shops',
        'Specific price rules', 'Specific prices', 'States', 'Stock availables', 'Stock movement reasons',
        'Stock movements', 'Stocks', 'Stores', 'Suppliers', 'Supply order details', 'Supply order histories',
        'Supply order receipt histories', 'Supply order states', 'Supply orders', 'Tags', 'Tax rule groups',
        'Tax rules', 'Taxes', 'Translated configurations', 'Warehouse product locations', 'Warehouses',
        'Weight ranges', 'Zones']


    def __init__(self, shop_url, api_key):
        self.shop_url = shop_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def _request_REST(self, query):
        resource = query['resource']
        url = f"{self.shop_url}/api/{resource}&display=full?output_format=JSON"
        if query['fil']:
            for key in query['fil'].keys():
                url += f"&filter[{key}]={query['fil'][key]}"
        try:
            response = self.session.get(url)
        except Exception as ex:
            raise PrestashopRESTConnectException('Error requesting URL "%s" (%s)' % (url, ex))

        match response.status_code:
            case 200:
                pass
            case 201:
                pass
            case 400:
                raise PrestashopRESTBadRequestException('Bad request')
            case 401:
                raise PrestashopRESTInvalidTokenException('Invalid API access token for shop')
            case 404:
                raise PrestashopRESTURLNotFoundException('The requested URL was not found on this server.')
            case _:
                raise PrestashopRESTException(
                    'Bad API response status code (%s): %s' % (response.status_code, response.content))
        try:
            response_data = response.json()
        except:
            raise PrestashopRESTException("Bad API response (JSON format)")

        if response_data:
            errors = response_data.get('errors')
            if errors:
                error_message = ''
                for err in errors:
                    try:
                        error_message += ' [%s]' % err['message']
                    except:
                        raise PrestashopRESTException('Bad API response ("errors" object format)')
                raise PrestashopRESTException('GraphQL query errors:%s' % error_message)
        else:
            raise PrestashopRESTException('No data available at this time！')
        return response_data

    def _request_REST_xml(self, query):
        global url
        resource = query['resource']
        if "products" in resource:
            url = f"{self.shop_url}/api/{resource}&display=full"
        try:
            response = self.session.get(url)
        except Exception as ex:
            raise PrestashopRESTConnectException('Error requesting URL "%s" (%s)' % (url, ex))

        match response.status_code:
            case 200:
                pass
            case 201:
                pass
            case 400:
                raise PrestashopRESTBadRequestException('Bad request')
            case 401:
                raise PrestashopRESTInvalidTokenException('Invalid API access token for shop')
            case 404:
                return None
            case _:
                raise PrestashopRESTException(
                    'Bad API response status code (%s): %s' % (response.status_code, response.content))
        try:
            response_data = response.content
        except:
            raise PrestashopRESTException("Bad API response (JSON format)")

        return response_data

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
        res_product = self._request_REST_xml(query1)
        if res_product:
            root = ET.fromstring(res_product)
            namespaces = {'xlink': 'http://www.w3.org/1999/xlink'}

            for elem in root.findall('.//*[@xlink:href]', namespaces):
                href_value = elem.get('{http://www.w3.org/1999/xlink}href')
                image_infos.append(href_value)
            return image_infos[0]
        else:
            return "No image"

    def get_app_access_scopes_all_information(self):
        acc_resources_all_information = []
        url = f"{self.shop_url}/api/"
        response = self.session.get(url)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for child in root.find('api'):
                resource_name = child.tag
                resource_href = child.attrib['{http://www.w3.org/1999/xlink}href']
                permissions = {k: v for k, v in child.attrib.items() if k != '{http://www.w3.org/1999/xlink}href'}
                acc_resource = {
                    "Resource": resource_name,
                    "Url": resource_href,
                    "Permissions": permissions
                }
                acc_resources_all_information .append(acc_resource)
        else:
            print(f"Failed to get API resources, status code: {response.status_code}")
        return acc_resources_all_information

    def get_app_access_scopes(self):
        acc_resources = []
        acc_resources_all_information = self.get_app_access_scopes_all_information()
        for acc_resource_all_information in acc_resources_all_information:
            acc_resources.append(acc_resource_all_information['Resource'].capitalize())
        return acc_resources

    def get_missing_app_access_scopes(self):
        not_acc_resources = []

        acc_resources = self.get_app_access_scopes()

        for requiredAppAccessScope in self._REQUIRED_APP_ACCESS_SCOPES:
            if requiredAppAccessScope not in acc_resources:
                not_acc_resources.append(requiredAppAccessScope)

        return not_acc_resources

    def get_address_by_id(self, address_id):
        """
        Get address by id
        :param address_id:
        :return: address info
        """
        query1 = {"resource": "addresses", "fil": {"id": address_id}}
        res_address = self._request_REST(query1)
        try:
            address_data = res_address['addresses'][0]
            if address_data:
                query2 = {"resource": "countries", "fil": {"id": address_data['id_country']}}
                country_data = self._request_REST(query2)["countries"][0]
                if country_data:
                    country_name = country_data['name']
                    eng_country_name = self.get_need_language(country_name, LangageType.ENGLISH_NAME)
                    query3 = {"resource": "zones", "fil": {"id": country_data["id_zone"]}}
                    zone_name = self._request_REST(query3)["zones"][0]["name"]
                    if zone_name:
                        address_info = {
                            "address1": address_data['address1'],
                            "address2": address_data['address2'],
                            "city": address_data['city'],
                            "company": address_data['company'],
                            "country": eng_country_name,
                            "firstName": address_data['firstname'],
                            "lastName": address_data['lastname'],
                            "zone": zone_name,
                            "postcode": address_data['postcode']
                        }
                        return address_info
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_order_states_by_id(self, sid):
        query1 = {"resource": "order_states", "fil": {"id": sid}}
        res_order_states = self._request_REST(query1)
        try:
            order_states_data = res_order_states['order_states'][0]
            if order_states_data:
                order_states_info = {
                    "name": self.get_need_language(order_states_data["name"], LangageType.ENGLISH_NAME),
                    "template": self.get_need_language(order_states_data["template"], LangageType.ENGLISH_NAME),
                    "paid": order_states_data["paid"]
                }
                return order_states_info
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_last_order(self, customer_id):
        """
        Get the latest order
        :param customer_id:
        :return: most_recent_order
        """
        query = {"resource": "orders", "fil": {"id_customer": customer_id}}
        res_order = self._request_REST(query)
        try:
            orders = res_order['orders']
            if orders:
                sorted_orders = sorted(orders, key=lambda x: datetime.strptime(x['date_add'], '%Y-%m-%d %H:%M:%S'),
                                       reverse=True)
                most_recent_order = sorted_orders[0]
                return most_recent_order
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_pon_by_pov(self, pov_id):
        query = {"resource": "product_options", "fil": ""}
        res_product_option = self._request_REST(query)
        try:
            product_options = res_product_option['product_options']
            if product_options:
                for product_option in product_options:
                    option_id_list = []
                    option_ids = product_option['associations']['product_option_values']
                    if option_ids:
                        for option_id in option_ids:
                            option_id_list.append(option_id['id'])
                        if pov_id in option_id_list:
                            return self.get_need_language(product_option['name'], LangageType.ENGLISH_NAME)
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_payment(self, order_reference):
        query = {"resource": "order_payments", "fil": {"order_reference": order_reference}}
        res_order_payments = self._request_REST(query)
        try:
            order_payments = res_order_payments['order_payments'][0]
            if order_payments:
                payment_info = {
                    "amount": order_payments["amount"],
                    "paymentMethod": order_payments["payment_method"],
                    "order_reference": order_payments["order_reference"],
                    "card_holder": order_payments["card_holder"],
                    "card_number": order_payments["card_number"],
                    "card_brand": order_payments["card_brand"],
                    "card_expiration": order_payments["card_expiration"],
                    "date_add": order_payments["date_add"]
                }
                return payment_info
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

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
        query = {"resource": "categories", "fil": {"id": int(cat_id)}}
        res_category = self._request_REST(query)
        try:
            name = res_category['categories'][0]['name']
            if name:
                check_name = self.get_need_language(name, l_type)
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_shop_name(self):
        query = {"resource": "shops", "fil": ""}
        res_shop = self._request_REST(query)
        try:
            shops = res_shop['shops']
            if shops:
                shop_names = []
                for shop in shops:
                    shop_names.append(shop['name'])
                return shop_names
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_shop_info(self):
        shop_infos = {}
        query = {"resource": "shops", "fil": ""}
        res_shop = self._request_REST(query)
        try:
            shops = res_shop['shops']
            if shops:
                for shop in shops:
                    shop_infos['name'] = shop['name']
                    query = {"resource": "categories", "fil": {"id": shop['id_category']}}
                    res_category = self._request_REST(query)
                    name = res_category['categories'][0]['name']
                    if name:
                        shop_infos['category'] = {}
                        english_name = name[0]['value']
                        french_name = name[1]['value']
                        shop_infos['category']['english_name'] = english_name
                        shop_infos['category']['french_name'] = french_name
                return shop_infos
        except:
            raise PrestashopRESTException('Bad API response (object format)')

        return None

    def get_product_categories(self):
        categories_names = {'english_name': [], 'french_name': []}
        query = {"resource": "categories", "fil": ""}
        res_cat = self._request_REST(query)
        try:
            product_categories = res_cat['categories']
            if product_categories:
                for category in product_categories:
                    english_name = category['name'][0]['value']
                    french_name = category['name'][1]['value']
                    categories_names['english_name'].append(english_name)
                    categories_names['french_name'].append(french_name)
                return categories_names
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_all_products(self):
        product_infos = []
        query = {"resource": "products", "fil": ""}
        res_product = self._request_REST(query)
        try:
            products = res_product['products']
            if products:
                for product in products:
                    english_des = self.get_need_language(product['description'], LangageType.ENGLISH_NAME)
                    english_title = self.get_need_language(product['name'], LangageType.ENGLISH_NAME)
                    image_url = self.get_product_image(self, product['id'])
                    # Show Only Sold Items
                    if product['available_for_order'] != '0':
                        product_info = {
                            "id": product['id'],
                            "productType": product['product_type'],
                            "description": english_des,
                            "title": english_title,
                            "imageUrl": image_url,
                            "price": product['price'],
                            "publishAt": product['date_add'],
                            "minPrice": product['price'],
                            "maxPrice": product['price']
                        }
                        product_infos.append(product_info)
                return product_infos
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_product_options(self, product_id):
        query1 = {"resource": "products", "fil": {"id": product_id}}
        res_product = self._request_REST(query1)
        try:
            product_available = res_product['products'][0]['available_for_order']
            if product_available:
                product_option = res_product['products'][0]['associations']['product_option_values']
                if product_option:
                    selected_options = []
                    for product_option_id_dict in product_option:
                        product_option_id = product_option_id_dict['id']
                        query2 = {"resource": "product_option_values", "fil": {"id": product_option_id}}
                        res_product_option = self._request_REST(query2)
                        product_option_value_id = product_option_id_dict['id']
                        if product_option_value_id:
                            product_option_name = self.get_pon_by_pov(product_option_value_id)
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
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_customer_information(self, email):
        query1 = {"resource": "customers", "fil": {"email": email}}
        res_cus = self._request_REST(query1)
        try:
            cus_info = res_cus['customers'][0]
            if cus_info:
                query2 = {"resource": "orders", "fil": {"id_customer": cus_info["id"]}}
                res_order = self._request_REST(query2)
                order_info = res_order['orders']
                if order_info:
                    last_order_id = self.get_last_order(cus_info['id'])['id']
                    query3 = {"resource": "addresses", "fil": {"id_customer": cus_info['id']}}
                    res_address = self._request_REST(query3)
                    address_info = res_address['addresses'][0]
                    if address_info:
                        query4 = {"resource": "countries", "fil": {"id": address_info['id_country']}}
                        country_info = self._request_REST(query4)["countries"][0]
                        if country_info:
                            country_name = country_info['name']
                            eng_country_name = self.get_need_language(country_name, LangageType.ENGLISH_NAME)
                            query5 = {"resource": "zones", "fil": {"id": country_info["id_zone"]}}
                            zone_name = self._request_REST(query5)["zones"][0]["name"]
                            if zone_name:
                                customer_infos = {
                                    "id": cus_info['id'],
                                    "firstname": cus_info['firstname'],
                                    "lastname": cus_info['lastname'],
                                    "createdAt": cus_info['date_add'],
                                    "lifetimeDuration": self.get_days(cus_info['date_add']),
                                    "numberOfOrders": len(order_info),
                                    "lastOrder": {
                                        "id": last_order_id
                                    },
                                    "defaultAddress": {
                                        "address1": address_info['address1'],
                                        "address2": address_info['address2'],
                                        "city": address_info['city'],
                                        "company": address_info['company'],
                                        "country": eng_country_name,
                                        "firstName": address_info['firstname'],
                                        "lastName": address_info['lastname'],
                                        "zone": zone_name,
                                        "postcode": address_info['postcode']
                                    }
                                }
                                return customer_infos
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None

    def get_customer_order(self, order_id, customer_id):
        query1 = {"resource": "orders", "fil": {"id": order_id, "id_customer": customer_id}}
        res_order = self._request_REST(query1)
        try:
            order_data = res_order['orders'][0]
            if order_data:
                delivery_address = self.get_address_by_id(order_data['id_address_delivery'])
                invoice_address = self.get_address_by_id(order_data['id_address_invoice'])
                order_state = self.get_order_states_by_id(order_data['current_state'])
                products = order_data["associations"]["order_rows"]
                products_info = []
                for product in products:
                    product_info = {
                        "name": product["product_name"],  # product_name
                        "currentQuantity": product["product_quantity"],  # product_quantity
                        "originalTotalSet": product["product_price"],  # product_price
                    }
                    products_info.append(product_info)
                query2 = {"resource": "order_carriers", "fil": {"id": order_id, "id_order": order_data["id"]}}
                res_order_carriers = self._request_REST(query2)
                order_carriers = res_order_carriers["order_carriers"][0]
                if order_carriers:
                    fulfillments = {
                        "trackingInfo": order_carriers["tracking_number"]
                    }
                    payment = self.get_payment(order_data["reference"])
                    transaction_info = {
                        "amount": payment["amount"],
                        "paymentMethod": order_state["template"],
                        "processedAt": payment["date_add"],
                        "status": order_state["name"],
                        "paymentDetails": {
                            "CardPaymentDetails": {
                                "name": payment["card_holder"],
                                "number": payment["card_number"],
                                "paymentMethodName": payment["card_brand"],
                                "expirationDate": payment["card_expiration"],
                            }
                        },
                    }
                    order_info = {
                        "id": order_data["id"],
                        "confirmationNumber": order_data["reference"],  # reference
                        "createAt": order_data["date_add"],  # date_add
                        "cancelledAt": "null",
                        "cancelReason": "null",
                        "closed": 0,
                        "closedAt": "null",
                        "billingAddressMatchesShippingAddress": 1 if invoice_address == delivery_address else 0,
                        "billingAddress": invoice_address,  # invoice
                        "shippingAddress": delivery_address,  # delivery
                        "fullyPaid": order_state["paid"],  # paid
                        "unpaid": order_state["paid"],  # paid
                        "totalDiscountsSet": order_data["total_discounts"],  # total_discounts
                        "totalPriceSet ": order_data["total_paid"],  # total_paid
                        "totalShippingPriceSet": order_data["total_shipping"],  # total_shipping
                        "lineItems": products_info,
                        "fulfillments": fulfillments,
                        "transactions": transaction_info,
                    }
                    return order_info
        except:
            raise PrestashopRESTException('Bad API response (object format)')
        return None


if __name__ == "__main__":
    shop_url = "http://localhost:8888/localinstallation"
    api_key = "3XMLLL1F19UEIYC44X8LZTTQCKZZ6W33"

    api = PrestashopREST(shop_url, api_key)

    # shop_name = api.get_shop_name()
    # print(f"Shop name: {shop_name}")

    # shop_info = api.get_shop_info()
    # print(f"Shop info: {shop_info}")

    # categories = api.get_product_categories()
    # print(f"Categories: {categories}")

    products = api.get_all_products()
    for product in products:
        print(product)

    # options = api.get_product_options(1)
    # print(options)

    # client_information = api.get_customer_information("pub@prestashop.com")
    # print(client_information)

    # order = api.get_customer_order(2, 2)
    # print(order)

    # all_acc_resources = api.get_app_access_scopes()
    # print(f"Accessible resources: {all_acc_resources}")
    #
    # all_not_acc_resources = api.get_missing_app_access_scopes()
    # print(f"Inaccessible resources: {all_not_acc_resources}")