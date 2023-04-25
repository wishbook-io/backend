import requests
import json
import logging
from datetime import datetime
from collections import OrderedDict
from django.db.models import Sum,Q,F
from api.v1.serializers import InvoiceSerializer
from api.models import (SalesOrder,SalesOrderItem,
                            Invoice,InvoiceItem,Shipment,
                            Warehouse,ShipRocketApiLog,
                            Catalog
                        )


logger = logging.getLogger(__name__)

def get_token():
    """
     get the access token from Shiprocket.
    """
    credentials    = {
      "email": "tech@wishbook.io",
      "password": "Wishbook5298"
    }
    auth           = requests.post('https://apiv2.shiprocket.in/v1/external/auth/login',data=credentials)
    return auth.json()['token']


def create_order_on_ship_rocket(order_id,length,breadth,height,weight, pickup_location, pickup_pincode, combine_multiple=False,order_ids = [],partial_value_list={}):
    """
        create order in ship rocket.
    """
    logger.info("creating order on ShipRocket with combined multiple %s  %s ", order_id,combine_multiple)
    try:
        order = SalesOrder.objects.get(pk=order_id)
        name_value_list = OrderedDict()
        if combine_multiple:
            name_value_list["order_id"] = ('-').join(order_ids)
        else:
            name_value_list["order_id"] = order_id
        name_value_list["order_date"]               = str(order.created_at)
        name_value_list["pickup_location"]          = pickup_location
        name_value_list["channel_id"]               = 49583
        name_value_list["billing_customer_name"]    = partial_value_list['billing_customer_name']
        name_value_list["billing_last_name"]        = partial_value_list['billing_last_name']
        name_value_list["billing_address"]          = partial_value_list['billing_address']
        name_value_list["billing_address_2"]        = partial_value_list['billing_address_2']
        name_value_list["billing_city"]             = partial_value_list['billing_city']
        name_value_list["billing_state"]            = partial_value_list['billing_state']
        name_value_list["billing_country"]          = order.ship_to.country.name
        name_value_list["billing_pincode"]          = partial_value_list['billing_pincode']
        name_value_list["billing_email"]            = "support@wishbook.io"
        name_value_list["billing_phone"]            = order.company.phone_number
        name_value_list["shipping_is_billing"]      = True
        items_list                                  = []
        if combine_multiple:
            orders                                      = SalesOrder.objects.filter(id__in=order_ids)
            name_value_list["sub_total"]                = int(combine_sub_total(orders))
            for order in orders:
                catalog_ids     = order.items.all().values_list('product__catalog', flat=True).distinct()
                catalogs        = Catalog.objects.filter(id__in=catalog_ids)
                for catalog in catalogs:
                    per_catalog                         = getCatalogInvoiceItem(order,catalog.id)
                    logger.info("per_catalog response for ShipRocket %s",str(per_catalog))
                    units                               = per_catalog.get('total_qty',0)
                    tax_per                             = per_catalog.get('tax_per',0)
                    discount                            = (per_catalog.get('total_disc',0))/units
                    per_catalog_price                   = ((per_catalog.get('total_amt',0))+(per_catalog.get('total_disc',0)))/units
                    item_value_list                     = OrderedDict()
                    item_value_list["name"]             = catalog.title
                    item_value_list["sku"]              = catalog.id
                    item_value_list["units"]            = units
                    item_value_list["selling_price"]    = int(per_catalog_price)
                    item_value_list["discount"]         = int(discount)
                    item_value_list["tax"]              = float(tax_per)
                    item_value_list["hsn"]              = per_catalog.get('hsn',"")
                    items_list.append(item_value_list)
        else:
            name_value_list["sub_total"]    = int(sub_total(order_id))
            catalog_ids                     = order.items.all().values_list('product__catalog', flat=True).distinct()
            catalogs                        = Catalog.objects.filter(id__in=catalog_ids)
            for catalog in catalogs:
                per_catalog                         = getCatalogInvoiceItem(order,catalog.id)
                logger.info("per_catalog response for ShipRocket %s",str(per_catalog))
                units                               = per_catalog.get('total_qty',0)
                tax_per                             = per_catalog.get('tax_per',0)
                discount                            = (per_catalog.get('total_disc',0))/units
                per_catalog_price                   = ((per_catalog.get('total_amt',0))+(per_catalog.get('total_disc',0)))/units
                item_value_list                     = OrderedDict()
                item_value_list["name"]             = catalog.title
                item_value_list["sku"]              = catalog.id
                item_value_list["units"]            = units
                item_value_list["selling_price"]    = int(per_catalog_price)
                item_value_list["discount"]         = int(discount)
                item_value_list["tax"]              = float(tax_per)
                item_value_list["hsn"]              = per_catalog.get('hsn',"")
                items_list.append(item_value_list)

        name_value_list["order_items"]              = items_list
        name_value_list["payment_method"]           = payment_method(order.order_type)
        name_value_list["shipping_charges"]         = 0
        name_value_list["giftwrap_charges"]         = 0
        name_value_list["transaction_charges"]      = 0
        name_value_list["total_discount"]           = 0
        name_value_list["length"]                   = length
        name_value_list["breadth"]                  = breadth
        name_value_list["height"]                   = height
        name_value_list["weight"]                   = weight
        name_value_list                             = json.dumps(name_value_list)

    except Exception as e:
        logger.error("Incorrect data send %s ", exc_info=True)
        return  {"message" : "Incorrect data send to ShipRocket  " + str(e), "status_code" : 500}

    try:
        token = get_token()
        order_response = requests.post('https://apiv2.shiprocket.in/v1/external/orders/create/adhoc',
                                            headers = {"Authorization": "Bearer "+ token,
                                            "accept": "application/json",
                                             "Content-Type": "application/json"},
                                             data = name_value_list
                                        )
        order_response =  order_response.json()
        logger.info("response by ShipRocket on create  %s ",str(order_response))
        ship_log                        = ShipRocketApiLog()
        ship_log.provider_api_response  = order_response
        ship_log.provider_access_type   = "CREATE"
        if combine_multiple:
            ship_log.wishbook_order_ids = ('-').join(order_ids)
        else:
            ship_log.wishbook_order_ids = order_id
        if (order_response.has_key("status")  and order_response["status"] == "NEW") or (order_response.has_key("status_code") and order_response['status_code'] in [1,2,3,12]):
            service_value_list                      = OrderedDict()
            service_value_list["pickup_postcode"]   = pickup_pincode
            service_value_list["delivery_postcode"] = int(order.ship_to.pincode)
            service_value_list["weight"]            = weight
            if order.order_type == "Prepaid":
                service_value_list["cod"] = 0
            else:
                service_value_list["cod"] = 1

            if combine_multiple:
                orders                               = SalesOrder.objects.filter(id__in=order_ids)
                service_value_list["declared_value"] = int(combine_sub_total(orders))
            else:
                service_value_list["declared_value"] = int(sub_total(order_id))

            service_value_list["order_id"]          =  order_response["order_id"]
            service_response                        = requests.get('https://apiv2.shiprocket.in/v1/external/courier/serviceability/',
                                                         headers = {"Authorization": "Bearer "+ token,
                                                         "accept": "application/json",
                                                         "Content-Type": "application/json"},
                                                         params =  service_value_list
                                                         )
            service_response                        =  service_response.json()
            service_response["ship_order_id"]       = order_response["order_id"]
            service_response["order_shipment_id"]   = order_response["shipment_id"]
            ship_log.provider_order_id              = order_response["order_id"]
            ship_log.provider_shipment_id           = order_response["shipment_id"]
            ship_log.provider_status                = "SUCCESS"
            ship_log.save()
            logger.info("service_response == " %(service_response))
            return service_response
        else:
            ship_log.provider_status                = "FAILED"
            ship_log.save()
            if order_response.has_key("status_code") and order_response['status_code'] == 5:
                return {"message" : "Order is Cancelled on ShipRocket", "status_code" : 500}
            logger.info("Incorrect data send to ShipRocket  %s %s %s ",str(order_response.get('message','')),str(order_response.get('errors','')),str(order_response.get('status_code',500)))
            return {"message" : str(order_response.get('message','')) + str(order_response.get('errors','')), "status_code" : 500}

    except Exception as e:
        logger.error('service_response Error:', exc_info=True)
        ship_log.provider_status = "FAILED"
        ship_log.save()
        return {"message" : "Some Error Occured While Creating an Order  " + str(e), "status_code" : 500}


def create_awb_on_ship_rocket(order_id, ship_order_id, order_shipment_id, courier_id, combine_multiple = False, order_ids = []):
    """
            {
          "shipment_id": [
                0
              ],
              "courier_id": 0
            }
    """
    try:
        token                           = get_token()
        awb_value_list  = {
                              "shipment_id": [
                                    order_shipment_id     #there can be multiple ids
                                  ],
                                  "courier_id": courier_id
                            }
        awb_value_list  =   json.dumps(awb_value_list)

        awb_response    = requests.post('https://apiv2.shiprocket.in/v1/external/courier/assign/awb',
                                            headers = {"Authorization": "Bearer "+ token,
                                            "accept": "application/json",
                                             "Content-Type": "application/json"},
                                             data = awb_value_list
                                        )
        awb_response      = awb_response.json()
        awb_code          =  awb_response.get('response',{}).get('data',{}).get('awb_code',None)
        courier_name      =  awb_response.get('response',{}).get('data',{}).get('courier_name',None)
        invoice_response  = genrate_order_invoice(ship_order_id,token)
        invoice_url       =  invoice_response.get("invoice_url",None)
        manifest_url      =  get_or_create_manifest(order_shipment_id,ship_order_id,token)
        label_url         =  generate_label(order_shipment_id,token)
        # tracking_details  =  str(label_url) + str(manifest_url)
        ship_log                        = ShipRocketApiLog()
        ship_log.provider_api_response  = awb_response
        ship_log.provider_access_type   = "AWB"
        ship_log.provider_shipment_id   = order_shipment_id
        ship_log.provider_order_id      = ship_order_id
        ship_log.provider_label_url     = label_url
        ship_log.provider_manifest_url  = manifest_url
        ship_log.provider_invoice_url   = invoice_url
        ship_log.provider_status        = "SUCCESS"


        from api.v1.views import InvoiceViewSet
        if combine_multiple:
            ship_log.wishbook_order_ids = ('-').join(order_ids)
            orders   =   SalesOrder.objects.filter(id__in=order_ids)
            for order in orders:
                invoice  =   Invoice.objects.filter(order_id=order.id).first()
                ivs = InvoiceViewSet(pk=invoice.id)
                request = {}
                request["data"] = {}
                request["data"]['tracking_number'] = awb_code
                # request["data"]['tracking_details'] = tracking_details
                request["data"]['logistics_provider'] = courier_name
                warehouse = Warehouse.objects.filter(company=order.seller_company).first()
                if warehouse:
                    request["data"]['warehouse'] = warehouse.id
                dispatch_response = ivs.dispatched(request,invoice.id)
        else:
            ship_log.wishbook_order_ids = order_id
            ship_log.save()
            invoice =  Invoice.objects.filter(order_id=order_id).first()
            ivs = InvoiceViewSet(pk=invoice.id)
            request = {}
            request["data"] = {}
            request["data"]['tracking_number'] = awb_code
            # request["data"]['tracking_details'] = tracking_details
            request["data"]['logistics_provider'] = courier_name
            order = SalesOrder.objects.get(pk=order_id)
            warehouse = Warehouse.objects.filter(company=order.seller_company).first()
            if warehouse:
                request["data"]['warehouse'] = warehouse.id
                dispatch_response = ivs.dispatched(request,invoice.id)
        result = {"label_url": label_url,"manifest_url": manifest_url, "invoice_url": invoice_url}
        logger.info("urls of ShipRocket after dispatiching invoices %s",str(result))
        return result
    except Exception as e:
        logger.error('AWB Error:', exc_info=True)
        ship_log.provider_status = "FAILED"
        ship_log.save()
        return {"message" : "Some Error Occured While Creating awb number " + str(e), "status_code" : 500}

def genrate_order_invoice(ship_order_id,token):
    """
            {
            "ids": [
                    0
                    ]
            }
    """
    try:
        invoice_value_list = {
        "ids": [
        ship_order_id
        ]
        }
        invoice_value_list = json.dumps(invoice_value_list)
        order_invoice   =   requests.post('https://apiv2.shiprocket.in/v1/external/orders/print/invoice',
        headers = {"Authorization": "Bearer "+ token,
        "accept": "application/json",
        "Content-Type": "application/json"},
        data = invoice_value_list
        )
        order_invoice   =   order_invoice.json()
        return order_invoice
    except Exception as e:
        logger.error('Invoice Error:', exc_info=True)
        return {"message" : "Some Error Occured While Creating an invoice on shiprocket " + str(e), "status_code" : 500}



def get_or_create_manifest(order_shipment_id,ship_order_id,token):
    """
        for get manifest->
                        {
              "order_ids": [
                0
              ]
            }
        for creating manifest->
                {
              "shipment_id": [
                123
              ]
            }
    """
    try:
        get_manifest_value_list  = {
        "order_ids": [
        ship_order_id
        ]
        }
        get_manifest_value_list  =   json.dumps(get_manifest_value_list)
        get_manifest_response    =   requests.post('https://apiv2.shiprocket.in/v1/external/orders/print/manifest',
        headers = {"Authorization": "Bearer "+ token,
        "accept": "application/json",
        "Content-Type": "application/json"},
        data = get_manifest_value_list
        )
        get_manifest_response    =  get_manifest_response.json()
        manifest_url             =  get_manifest_response['data']

        if len(manifest_url) > 0:
            return manifest_url
            create_manifest_value_list  = {
            "shipment_id": [
            order_shipment_id
            ]
            }
            create_manifest_value_list  =   json.dumps(create_manifest_value_list)
            create_manifest_response    =    requests.post('https://apiv2.shiprocket.in/v1/external/manifests/generate',
            headers = {"Authorization": "Bearer "+ token,
            "accept": "application/json",
            "Content-Type": "application/json"},
            data = create_manifest_value_list
            )
            create_manifest_response    =   create_manifest_response.json()
            manifest_url                =  create_manifest_response.get('manifest_url',None)
            return manifest_url
    except Exception as e:
        logger.error('Manifest Error:', exc_info=True)
        return {"message" : "Some Error Occured While getting manifest url " + str(e), "status_code" : 500}

def generate_label(order_shipment_id,token):
    """
            {
          "shipment_ids": [
            0
          ]
        }
    """
    label_value_list           =  {
                                      "shipment_id": [
                                        order_shipment_id
                                      ]
                                    }
    label_value_list           =   json.dumps(label_value_list)
    generate_label_response    = requests.post('https://apiv2.shiprocket.in/v1/external/courier/generate/label',
                                                headers = {"Authorization": "Bearer "+ token,
                                                "accept": "application/json",
                                                 "Content-Type": "application/json"},
                                                 data = label_value_list
                                                 )
    generate_label_response    = generate_label_response.json()
    label_url                  =  generate_label_response.get('label_url',None)
    return label_url



def get_pickup_locations():
    token = get_token()
    pickup_location_response = requests.get('https://apiv2.shiprocket.in/v1/external/settings/company/pickup',
                                                 headers = {"Authorization": "Bearer "+ token,
                                                 "accept": "application/json",
                                                 "Content-Type": "application/json"},
                                                 )

    pickup_location_response = pickup_location_response.json()
    return pickup_location_response

def get_tracking_details(awb_code):
    token = get_token()
    tracking_details_response = requests.get('https://apiv2.shiprocket.in/v1/external/courier/track/awb/' + str(awb_code),
                                                 headers = {"Authorization": "Bearer "+ token,
                                                 "accept": "application/json",
                                                 "Content-Type": "application/json"},
                                                 )
    tracking_details_response = tracking_details_response.json()
    return tracking_details_response

def payment_method(order_type):
    if order_type == "Credit":
        return "COD"
    return order_type


def combine_total_products(orders):
    total_products = 0
    for order in orders:
        total_products += order.total_products()
    return total_products

def combine_selling_price_per_item(orders):
    try:
        shipping_charge   = Invoice.objects.filter(order=orders[0]).aggregate(Sum('shipping_charges')).get('shipping_charges__sum', 0)
        if shipping_charge is None:
            shipping_charge = 0
        total_amount = 0
        total_products = 0
        for order in orders:
            total_amount += Invoice.objects.filter(order=order).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
            total_products += order.total_products()
        total_amount = total_amount - shipping_charge*(len(orders) - 1)
        combine_per_item_price = total_amount/total_products
        return combine_per_item_price
    except Exception as e:
        return 0

def selling_price_per_item(order):
    try:
        total_amount = Invoice.objects.filter(order=order).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
        return total_amount/order.total_products()
    except Exception as e:

        return 0


def selling_price_per_catalog(order,id):
    try:
        order_item_ids  = SalesOrderItem.objects.filter(sales_order=order).filter(Q(product__catalog__id = id)).values_list('id', flat=True).distinct()
        total_amount    = InvoiceItem.objects.filter(order_item_id__in=order_item_ids).aggregate(Sum('rate')).get('rate__sum', 0)
        return total_amount
    except Exception as e:

        return 0


def discount_price_per_catalog(order,id):
    try:
        order_item_ids  = SalesOrderItem.objects.filter(sales_order=order).filter(Q(product__catalog__title = id)).values_list('id', flat=True).distinct()
        discount_amount = InvoiceItem.objects.filter(order_item_id__in=order_item_ids).aggregate(Sum('discount')).get('discount__sum', 0)
        return discount_amount
    except Exception as e:

        return 0


def getCatalogInvoiceItem(order,catalog_id):
    try:
        order_item_ids          = SalesOrderItem.objects.filter(sales_order=order).filter(Q(product__catalog = catalog_id)).values_list('id', flat=True).distinct()
        per_catalog             = InvoiceItem.objects.filter(order_item_id__in=order_item_ids).aggregate(total_qty = Sum('qty'), total_rate = Sum('amount'), total_disc = Sum('discount'), total_tax1 =   Sum('tax_value_1'),total_tax2 =   Sum('tax_value_2'),total_amt = Sum('total_amount'))
        tax_code                = InvoiceItem.objects.filter(order_item_id__in=order_item_ids).values_list('tax_class_1__tax_code__tax_code',flat=True).distinct()
        tax                     = per_catalog['total_tax1'] + per_catalog['total_tax2']
        tax_per                 = (tax*100)/(per_catalog['total_amt'] - per_catalog['total_disc'])
        per_catalog['tax_per']  = tax_per
        if tax_code:
            per_catalog['hsn']  =  tax_code[0]
        logger.info('ShipRocket per_catalog: %s' %(per_catalog))
        return per_catalog
    except Exception as e:
        logger.error('ShipRocket getCatalogInvoiceItem Error:', exc_info=True)
        return None

def tax_per_catalog(order_id,id):
    total_tax       = Invoice.objects.filter(order_id=order_id).aggregate(Sum('taxes')).get('taxes__sum', 0)
    order_item_ids  = SalesOrderItem.objects.filter(sales_order_id=order_id).filter(Q(product__catalog__title = id)).values_list('id', flat=True).distinct()
    tax1            = InvoiceItem.objects.filter(order_item_id__in=order_item_ids).aggregate(Sum('tax_value_1')).get('tax_value_1__sum', 0)
    tax2            = InvoiceItem.objects.filter(order_item_id__in=order_item_ids).aggregate(Sum('tax_value_2')).get('tax_value_2__sum', 0)
    tax_per = 0
    if not ((tax1 + tax2)==0):
        tax_per = ((tax1 + tax2)*100)/total_tax
    return tax_per



def sub_total(order_id):
    try:
        sub_total = Invoice.objects.filter(order_id=order_id).aggregate(shipping_charges=Sum('shipping_charges'),total_amount=Sum('total_amount'))
        return (sub_total['total_amount'] - sub_total['shipping_charges'])
    except Exception as e:
        logger.error('ShipRocket sub_total Error:', exc_info=True)
        return 0

def combine_sub_total(orders):
    try:
        sub_total = Invoice.objects.filter(order__id__in=orders).aggregate(shipping_charges=Sum('shipping_charges'),total_amount=Sum('total_amount'))
        return (sub_total['total_amount'] - sub_total['shipping_charges'])
    except Exception as e:
        logger.error('ShipRocket combine_sub_total Error:', exc_info=True)
        return 0

def address_line_1(order):
    if len(order.ship_to.street_address) > 50:
        address =  order.ship_to.street_address
        arr     =  address.split()
        address_line_1 = ""
        for add1 in arr:
            if len(address_line_1 +  add1) < 50 :
                address_line_1 = address_line_1 + " " + add1
            else:
                break
        logger.info("ShipRocket address_line_1 ====  %s ",str(address_line_1))
        return address_line_1
    return order.company.name

def address_line_2(order):
    if len(order.ship_to.street_address) > 50:
        address =  order.ship_to.street_address
        arr     =  address.split()
        address_line_2 = ""
        temp = ""
        for add1 in arr:
            if len(temp +  add1) < 50 :
                temp = temp + " " + add1
            else:
                if len(address_line_2 +  add1) < 50 :
                    address_line_2 = address_line_2 + " " + add1
                else:
                    break
        logger.info("ShipRocket address_line_2 ====  %s ",str(address_line_2))
        return address_line_2
    return order.ship_to.street_address
def last_name(order):
    if order.company.chat_admin_user.last_name is None or order.company.chat_admin_user.last_name == '':
        name = order.company.chat_admin_user.first_name.split(" ")
        if len(name) > 1:
            return " ".join(name[1:])
        return order.company.chat_admin_user.first_name
    return order.company.chat_admin_user.last_name

def catalog_peice(order,id):
    pieces = order.items.filter(Q(product__catalog__title=id)).aggregate(Sum('quantity')).get('quantity__sum', 0)
    if pieces is None:
        pieces = 0
    return pieces


def check_values_from_frontend(order_id):
    order = SalesOrder.objects.get(id=order_id)
    name_value_list                             = {}
    name_value_list["billing_customer_name"]    = order.company.chat_admin_user.first_name
    name_value_list["billing_last_name"]        = last_name(order)
    if order.ship_to:
        if order.ship_to.street_address:
            name_value_list["billing_address"]   = address_line_1(order)
            name_value_list["billing_address_2"] = address_line_2(order)
        name_value_list["billing_city"]     = order.ship_to.city.city_name
        name_value_list["billing_state"]    = order.ship_to.state.state_name
        name_value_list["billing_country"]  = order.ship_to.country.name
        name_value_list["billing_pincode"]  = int(order.ship_to.pincode)
    name_value_list["billing_email"]    = "support@wishbook.io"
    name_value_list["billing_phone"]    = order.company.phone_number

    return name_value_list




# service_response   = {
#                       "status": 200,
#                       "data": {
#                         "is_recommendation_enabled": 1,
#                         "recommended_by": {
#                           "id": 1,
#                           "title": "Best in price"
#                         },
#                         "recommended_courier_company_id": 42,
#                         "available_courier_companies": [
#                           {
#                             "courier_company_id": 42,
#                             "courier_name": "FEDEX-SL",
#                             "is_rto_address_available": False,
#                             "rate": 49.6,
#                             "is_surface": True,
#                             "rating": 3.7,
#                             "estimated_delivery_days": "1.81",
#                             "delivery_performance": 100,
#                             "cod": 1,
#                             "entry_tax": 0
#                           },
#                           {
#                             "courier_company_id": 40,
#                             "courier_name": "GATI-SURFACE",
#                             "is_rto_address_available": False,
#                             "rate": 55,
#                             "is_surface": True,
#                             "rating": 3.2,
#                             "estimated_delivery_days": "3.93",
#                             "delivery_performance": 100,
#                             "cod": 1,
#                             "entry_tax": 0
#                           },
#                           {
#                             "courier_company_id": 12,
#                             "courier_name": "FEDEX-SURFACE",
#                             "is_rto_address_available": False,
#                             "rate": 144,
#                             "is_surface": True,
#                             "rating": 3.4,
#                             "estimated_delivery_days": "1.79",
#                             "delivery_performance": 80,
#                             "cod": 1,
#                             "entry_tax": 0
#                           },
#                           {
#                             "courier_company_id": 39,
#                             "courier_name": "DELHIVERY-SURFACE",
#                             "is_rto_address_available": True,
#                             "rate": 149,
#                             "is_surface": True,
#                             "rating": 0,
#                             "estimated_delivery_days": "Not Available",
#                             "delivery_performance": 0,
#                             "cod": 1,
#                             "entry_tax": 0
#                           }
#                         ]
#                       }
#                     }
# service_response["ship_order_id"] = 12345
# service_response["order_shipment_id"] = 4321
# print "service_response",service_response
#
# {u'status_code': 400, u'message': u'Inventory sync is turned off. Please add a manual order!'}
