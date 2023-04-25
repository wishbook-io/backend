from django.conf import settings
from django.template.loader import render_to_string
from notifier.backends import BaseBackend

from api.common_functions import *
import random
from push_notifications.models import GCMDevice ,APNSDevice
import urllib
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader

from django.db.models import Sum

from datetime import datetime, date, timedelta
from api.models import *
import time


class SMS(BaseBackend):
    name = 'sms-notification'
    display_name = 'SMSNotification'
    description = 'Send SMS'

    def send(self, user, context=None):
        print "=== SMS ==="
        notification_type = self.notification
        mobile_number = user.userprofile.country.phone_code+user.userprofile.phone_number

        if UnsubscribedNumber.objects.filter(country=user.userprofile.country, phone_number=user.userprofile.phone_number).exists():
            return True

        print user.userprofile.phone_number
        if str(notification_type) == "otp": #not using
            print "=otp="
            #url = smsUrl()% (mobile_number)

            #template = smsTemplates("sendOTP")% (context['otp'])
            #smsSend([mobile_number], template, True)
            sendOTP(str(mobile_number), str(context['otp']))
            #smsSendICubes.apply_async(([mobile_number], template, True), expires=datetime.now() + timedelta(days=2))
            '''template = urllib.quote_plus(template)

            url = url+template
            try:
                sendsmart= requests.get(url)

                logger.info(str(url))
                logger.info(str(sendsmart))
                logger.info(str(sendsmart.text))

                if sendsmart.text != "Sent.":
                    mail_status = send_mail("SMS sendsmart", "Error = "+str(sendsmart.text)+" & mobile no = "+str(mobile_number)+" & OTP = "+str(context['otp']), settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
                    logger.info(str(mail_status))

                    sendsmart= requests.get(url)

                return sendsmart

            except Exception:
                return "Send Otp Failed to "+str(mobile_number)'''
        elif str(notification_type) == "sales-order": #not using
            print "=sales-order="
            #url = smsUrl()% (user.userprofile.country.phone_code+user.userprofile.phone_number)
            otp = getLastOTP(user.userprofile)
            usersmsurl = str(context['order_url']) + '&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
            time.sleep(1)
            usersmsurl = urlShortener(usersmsurl)

            template = smsTemplates("salesOrder_sales")% (str(context['table_id']), context['company_info'], usersmsurl)
            smsSend([mobile_number], template)
            #smsSendICubes.apply_async(([mobile_number], template), expires=datetime.now() + timedelta(days=2))
            '''template = urllib.quote_plus(template)

            url = url+template
            sendsmart= requests.get(url)'''
        elif str(notification_type) == "purchase-order": #not using
            print "=purchase-order="
            #url = smsUrl()% (user.userprofile.country.phone_code+user.userprofile.phone_number)

            template = smsTemplates("salesOrder_purchase")% (str(context['table_id']))
            smsSend([mobile_number], template)
            #smsSendICubes.apply_async(([mobile_number], template), expires=datetime.now() + timedelta(days=2))
            '''template = urllib.quote_plus(template)

            url = url+template
            sendsmart= requests.get(url)'''
        elif str(notification_type) == "buyer-request":#not using
            print "=buyer-request="
            #url = smsUrl()% (user.userprofile.country.phone_code+user.userprofile.phone_number)

            otp = getLastOTP(user.userprofile)
            usersmsurl = 'https://app.wishbooks.io/m?type=supplier&id='+str(context['table_id']) + '&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
            time.sleep(1)
            usersmsurl = urlShortener(usersmsurl)

            template = smsTemplates("requestNotification_buyer")% (context['company_name'], usersmsurl)
            smsSend([mobile_number], template)
            #smsSendICubes.apply_async(([mobile_number], template), expires=datetime.now() + timedelta(days=2))
            '''template = urllib.quote_plus(template)

            url = url+template
            sendsmart= requests.get(url)'''
        elif str(notification_type) == "supplier-request":#not using
            print "=supplier-request="
            #url = smsUrl()% (user.userprofile.country.phone_code+user.userprofile.phone_number)

            otp = getLastOTP(user.userprofile)
            usersmsurl = 'https://app.wishbooks.io/m?type=buyer&id='+str(context['table_id'])+'&m='+str(user.userprofile.phone_number)+'&o='+str(otp)
            time.sleep(1)
            usersmsurl = urlShortener(usersmsurl)

            template = smsTemplates("requestNotification_supplier")% (context['company_name'], usersmsurl)
            smsSend([mobile_number], template)
            #smsSendICubes.apply_async(([mobile_number], template), expires=datetime.now() + timedelta(days=2))
            '''template = urllib.quote_plus(template)

            url = url+template
            sendsmart= requests.get(url)'''
        elif str(notification_type) == "order-status": #not using
            print "=order-status="
            #url = smsUrl()% (user.userprofile.country.phone_code+user.userprofile.phone_number)

            template = smsTemplates("salesOrder_status")% (str(context['table_id']), context['status'])
            smsSend([mobile_number], template)
            #smsSendICubes.apply_async(([mobile_number], template), expires=datetime.now() + timedelta(days=2))
            '''template = urllib.quote_plus(template)

            url = url+template
            sendsmart= requests.get(url)'''

        '''if sendsmart.text == "Sent.":
            smsTrasaction("sendsmart", 1)'''

        return True

class InApp(BaseBackend):
    name = 'mobile-notification'
    display_name = 'MobileNotification'
    description = 'Send Mobile Notification'

    def send(self, user, context=None):
        notification_type = self.notification
        print "=== InApp ==="

        rno = random.randrange(100000, 999999, 1)
        image = settings.MEDIA_URL+"logo-single.png"

        if str(notification_type) == "sales-order": #not using
            print "=sales-order="
            if settings.TASK_QUEUE_METHOD == 'celery':
                notificationSend.apply_async(([user.id], "You have received an order "+str(context['table_id'])+" from "+context['company_info'], {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']}), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.notificationSend',
                    [user.id], "You have received an order "+str(context['table_id'])+" from "+context['company_info'], {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']}
                )

            '''device = GCMDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message("You have received an order "+context['order_number']+" from "+context['company_info'], extra={"notId": rno, "title":"Sales Order", "push_type":"promotional", "image":image})
                except Exception:
                    pass
            device = APNSDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message("You have received an order "+context['order_number']+" from "+context['company_info'], extra={"notId": rno, "title":"Sales Order", "push_type":"promotional", "image":image})
                except Exception:
                    pass'''
        elif str(notification_type) == "purchase-order":#not using
            print "=purchase-order="
            if settings.TASK_QUEUE_METHOD == 'celery':
                notificationSend.apply_async(([user.id], "Your order "+str(context['table_id'])+" has been successfully placed", {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']}), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.notificationSend',
                    [user.id], "Your order "+str(context['table_id'])+" has been successfully placed", {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']}
                )

            '''device = GCMDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message("Your order "+context['order_number']+" has been successfully placed", extra={"notId": rno, "title":"Purchase Order", "push_type":"promotional", "image":image})
                except Exception:
                    pass
            device = APNSDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message("Your order "+context['order_number']+" has been successfully placed", extra={"notId": rno, "title":"Purchase Order", "push_type":"promotional", "image":image})
                except Exception:
                    pass'''
        elif str(notification_type) == "buyer-request":#not using
            print "=buyer-request="
            if settings.TASK_QUEUE_METHOD == 'celery':
                notificationSend.apply_async(([user.id], context['company_name']+" has added you as a Buyer on Wishbook", {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.notificationSend',
                    [user.id], context['company_name']+" has added you as a Buyer on Wishbook", {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}
                )
            '''device = GCMDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message(context['company_name']+" has added you as a Buyer on Wishbook", extra={"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
                except Exception:
                    pass
            device = APNSDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message(context['company_name']+" has added you as a Buyer on Wishbook", extra={"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
                except Exception:
                    pass'''
        elif str(notification_type) == "supplier-request":#not using
            print "=supplier-request="
            if settings.TASK_QUEUE_METHOD == 'celery':
                notificationSend.apply_async(([user.id], context['company_name']+" has added you as a Supplier on Wishbook", {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.notificationSend',
                    [user.id], context['company_name']+" has added you as a Supplier on Wishbook", {"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']}
                )

            '''device = GCMDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message(context['company_name']+" has added you as a Supplier on Wishbook", extra={"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
                except Exception:
                    pass
            device = APNSDevice.objects.filter(user=user,active=True)
            if device:
                try:
                    status = device.send_message(context['company_name']+" has added you as a Supplier on Wishbook", extra={"notId": context['notId'], "push_type":context['push_type'], "company_id":context['company_id'], "table_id":context['table_id'], "title":context['title'], "company_image":context['company_image']})
                except Exception:
                    pass'''
        elif str(notification_type) == "share":#not using
            print "share"
            print "notifier backend"
            message = '%s has shared with you a catalog - %s'% (context['selling_company_name'], context['message'])
            #sendNotifications([user.id], message, {"push_id": context['push_id'],"notId":context['notId'],"push_type":context['push_type'],"image":context['image'], "company_image":context['company_image'], "title":context['title'], "name":context['name'], "table_id": context['table_id']})
            if settings.TASK_QUEUE_METHOD == 'celery':
                notificationSend.apply_async(([user.id], message, {"push_id": context['push_id'],"notId":context['notId'],"push_type":context['push_type'],"image":context['image'], "company_image":context['company_image'], "title":context['title'], "name":context['name'], "table_id": context['table_id']}), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.notificationSend',
                    [user.id], message, {"push_id": context['push_id'],"notId":context['notId'],"push_type":context['push_type'],"image":context['image'], "company_image":context['company_image'], "title":context['title'], "name":context['name'], "table_id": context['table_id']}
                )

        elif str(notification_type) == "order-status":#not using
            print "=order-status="
            #url = smsUrl()% (user.userprofile.country.phone_code+user.userprofile.phone_number)
            if settings.TASK_QUEUE_METHOD == 'celery':
                notificationSend.apply_async(([user.id], "Your order "+str(context['table_id'])+" is "+context['status']+". Track details by logging into Wishbook. Thank you for choosing us.", {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']}), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.notificationSend',
                    [user.id], "Your order "+str(context['table_id'])+" is "+context['status']+". Track details by logging into Wishbook. Thank you for choosing us.", {"notId": rno, "title":context['title'], "push_type":"promotional", "image":image, "table_id": context['table_id']}
                )

        return True

class EmailBackend(BaseBackend):
    name = 'email'
    display_name = 'Email'
    description = 'Send Email'
    def send(self, user, context=None):
        notification_type = self.notification
        print "=== EmailBackend ==="
        if str(notification_type) == "sales-order":#not using
            if "@wishbooks.io" not in user.email:
                print "=sales-order="
                try:
                    html_message = loader.render_to_string('email_templates/received_order.html', context)

                    #mail_status = send_mail("You got an order from "+context['buyer_name'], "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
                    if settings.TASK_QUEUE_METHOD == 'celery':
                        emailSend.apply_async(("You got an order from "+context['buyer_name'], "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message), expires=datetime.now() + timedelta(days=2))
                    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                        task_id = async(
                            'api.tasks.emailSend',
                            "You got an order from "+context['buyer_name'], "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message
                        )

                except Exception:
                    pass
        elif str(notification_type) == "purchase-order":#not using
            if "@wishbooks.io" not in user.email:
                print "=purchase-order="
                try:
                    html_message = loader.render_to_string('email_templates/purchase_order.html', context)

                    #mail_status = send_mail("Your order "+context['order_number']+" has been successfully placed", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
                    if settings.TASK_QUEUE_METHOD == 'celery':
                        emailSend.apply_async(("Your order "+str(context['table_id'])+" has been successfully placed", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message), expires=datetime.now() + timedelta(days=2))
                    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                        task_id = async(
                            'api.tasks.emailSend',
                            "Your order "+str(context['table_id'])+" has been successfully placed", "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message
                        )

                except Exception:
                    pass
        return True

class Chat(BaseBackend):
    name = 'chat'
    display_name = 'Chat'
    description = 'Chat Message'

    def send(self, user, context=None):
        notification_type = self.notification
        print "=== Chat ==="
        if str(notification_type) == "sales-order":#not using
            print "=sales-order="
            r = chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":"You have received an order "+str(context['table_id'])+" from "+context['company_info']})
        elif str(notification_type) == "purchase-order":#not using
            print "=purchase-order="
            r = chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":"Your order "+str(context['table_id'])+" has been successfully placed"})
        elif str(notification_type) == "buyer-request":#not using
            print "=buyer-request="
            r = chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":context['company_name']+" has added you as a Buyer"})
        elif str(notification_type) == "supplier-request":#not using
            print "=supplier-request="
            r = chat_send_message({"ofUserId":context['username'], "to":str(user.username), "message":context['company_name']+" has added you as a Supplier"})

        return True
