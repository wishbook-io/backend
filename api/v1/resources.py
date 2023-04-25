from import_export import resources
from import_export.fields import Field
from api.models import SalesOrder,Invoice
from django.db.models import Sum

class SalesOrderShipRocketResource(resources.ModelResource):
    id                                      = Field(attribute='id', column_name='*Order Id')
    created_at                              = Field(attribute='created_at',
                                                column_name='Order Date as dd-mm-yyyy hh:MM')
    payment_method                          = Field(attribute='payment_method',
                                                column_name='*Payment Method(COD/Prepaid)')
    company__chat_admin_user__first_name    = Field(attribute='company__chat_admin_user__first_name',
                                                column_name='*Customer First Name')
    company__chat_admin_user__last_name     = Field(attribute='company__chat_admin_user__last_name',
                                                column_name='*Customer Last Name')
    company__email                          = Field(attribute='company__email',
                                                column_name='*Email')
    company__phone_number                   = Field(attribute='company__phone_number',
                                                column_name='*Customer Mobile')
    address_line_1                          = Field(attribute='address_line_1',
                                                column_name='*Shipping Address Line 1')
    address_line_2                          = Field(attribute='address_line_2',
                                                column_name='*Shipping Address Line 2')
    ship_to__country__name                  = Field(attribute='ship_to__country__name',
                                                column_name='*Shipping Address Country')
    ship_to__state__state_name              = Field(attribute='ship_to__state__state_name',
                                                column_name='*Shipping Address State')
    ship_to__city__city_name                = Field(attribute='ship_to__city__city_name',
                                                column_name='*Shipping Address City')
    ship_to__pincode                        = Field(attribute='ship_to__pincode',
                                                column_name='*Shipping Address Postcode')
    bill_to__name                           = Field(attribute='address_line_1',
                                                column_name='Billing Address Line 1')
    bill_to__street_address                 = Field(attribute='address_line_2',
                                                column_name='Billing Address Line 2')
    bill_to__country__name                  = Field(attribute='ship_to__country__name',
                                                column_name='Billing Address Country')
    bill_to__state__state_name              = Field(attribute='ship_to__state__state_name',
                                                column_name='Billing Address State')
    bill_to__city__city_name                = Field(attribute='ship_to__city__city_name',
                                                column_name='Billing Address City')
    bill_to__pincode                        = Field(attribute='ship_to__pincode',
                                                column_name='Billing Address Postcode')
    channel                                 = Field(attribute='channel', column_name='*Channel')
    master_sku                              = Field(attribute='master_sku', column_name='*Master SKU')
    product_name                            = Field(attribute='product_name', column_name='*Product Name')
    product_quantity                        = Field(attribute='product_quantity',
                                                column_name='*Product Quantity')
    tax                                     = Field(attribute='tax', column_name='Tax %')
    selling_price_per_item                  = Field(attribute='selling_price_per_item',
                                                column_name='*Selling Price(Per Unit Item, Inclusive of Tax)')
    discount_per_unit                       = Field(attribute='discount_per_unit',
                                                column_name='Discount(Per Unit Item)')
    shipping_charges                        = Field(attribute='shipping_charges',
                                                column_name='Shipping Charges(Per Order)')
    cod_charges                             = Field(attribute='cod_charges',
                                                column_name='COD Charges(Per Order)')
    gift_wrap_charges                       = Field(attribute='gift_wrap_charges',
                                                column_name='Gift Wrap Charges(Per Order)')
    total_discount_per_order                = Field(attribute='total_discount_per_order',
                                                column_name='Total Discount (Per Order)')
    length                                  = Field(attribute='length', column_name='*Length (cm)')
    breadth                                 = Field(attribute='breadth', column_name='*Breadth (cm)')
    height                                  = Field(attribute='height', column_name='*Height (cm)')
    weight                                  = Field(attribute='weight',
                                                column_name='Weight Of Shipment(kg)')
    send_notification                       = Field(attribute='send_notification',
                                                column_name='Send Notification(True/False)')
    comment                                 = Field(attribute='comment', column_name='Comment')
    hsn_code                                = Field(attribute='hsn_code', column_name='HSN Code')

    class Meta:
        model = SalesOrder
        fields = ('id',
        'created_at',
        'company__chat_admin_user__first_name',
        'company__chat_admin_user__last_name',
        'company__phone_number',
        'ship_to__country__name',
        'ship_to__state__state_name',
        'ship_to__city__city_name',
        'ship_to__pincode',
        'bill_to__name',
        'bill_to__street_address',
        'bill_to__country__name',
        'bill_to__state__state_name',
        'bill_to__city__city_name',
        'bill_to__pincode',
        )
        export_order = (
        'id',
        'created_at',
        'channel',
        'payment_method',
        'company__chat_admin_user__first_name',
        'company__chat_admin_user__last_name',
        'company__email',
        'company__phone_number',
        'address_line_1',
        'address_line_2',
        'ship_to__country__name',
        'ship_to__state__state_name',
        'ship_to__city__city_name',
        'ship_to__pincode',
        'bill_to__name',
        'bill_to__street_address',
        'bill_to__country__name',
        'bill_to__state__state_name',
        'bill_to__city__city_name',
        'bill_to__pincode',
        'master_sku',
        'product_name',
        'product_quantity',
        'tax',
        'selling_price_per_item',
        'discount_per_unit',
        'shipping_charges',
        'cod_charges',
        'gift_wrap_charges',
        'total_discount_per_order',
        'length',
        'breadth',
        'height',
        'weight',
        'send_notification',
        'comment',
        'hsn_code',
        )
    def dehydrate_payment_method(self, order):
        if order.order_type == "Credit":
            return "COD"
        return order.order_type

    def dehydrate_product_quantity(self, order):
        return order.total_products()

    # def dehydrate_product_tax(self, order):
    #     invoice = Invoice.objects.filter(order=order).first()
    #     return 0

    def dehydrate_selling_price_per_item(self, order):
        try:
            total_amount = Invoice.objects.filter(order=order).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
            # total        = Invoice.objects.filter(order=order).aggregate(Sum('shipping_charges')).get('shipping_charges__sum', 0)
            # if total is None:
            #     total = 0
            # total_amount  += total
            return total_amount/order.total_products()
        except Exception as e:
            return ''

    def dehydrate_shipping_charges(self, order):
        # total = Invoice.objects.filter(order=order).aggregate(Sum('shipping_charges')).get('shipping_charges__sum', 0)
        # print "shipping_amount",total
        # if total is None:
        #     total = 0
        return ''

    def dehydrate_channel(self, order):
        return 'Custom'

    def dehydrate_length(self, order):
        return 10

    def dehydrate_breadth(self, order):
        return 10

    def dehydrate_height(self, order):
        return 10

    def dehydrate_weight(self, order):
        return 1

    def dehydrate_send_notification(self, order):
        return False

    def dehydrate_master_sku(self, order):
        sku = order.items.all().values_list('product__catalog__id', flat=True).distinct()
        return sku[0]

    def dehydrate_product_name(self, order):
        catalog_names = order.items.all().values_list('product__catalog__title', flat=True).distinct()
        return catalog_names[0]

    def dehydrate_company__chat_admin_user__last_name(self, order):
        if order.company.chat_admin_user.last_name is None or order.company.chat_admin_user.last_name == '':
            name = order.company.chat_admin_user.first_name.split(" ")
            if len(name) > 1:
                return " ".join(name[1:])
            return order.company.chat_admin_user.first_name
        return order.company.chat_admin_user.last_name

    def dehydrate_company__email(self, order):
        return "support@wishbook.io"

    def dehydrate_address_line_1(self, order):
        if len(order.ship_to.street_address) > 50:
            address =  order.ship_to.street_address
            arr     =  address.split()
            address_line_1 = ""
            for add1 in arr:
                if len(address_line_1 +  add1) < 50 :
                    address_line_1 = address_line_1 + " " + add1
                else:
                    break
        return order.company.name

    def dehydrate_address_line_2(self, order):

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
            return address_line_2
        return order.ship_to.street_address
