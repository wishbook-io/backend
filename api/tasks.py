from __future__ import absolute_import
#from __future__ import print_function
from celery import shared_task

from celery.decorators import task
from celery.exceptions import *
import celery

from datetime import datetime, date, time, timedelta
from rest_framework import serializers

import requests
import grequests
from django.conf import settings
import json
import urllib

from api.models import *
from django.core.mail import send_mail, EmailMessage

import logging
logger = logging.getLogger(__name__)

import pycurl, json
from cStringIO import StringIO

from django_q.tasks import async, result
from django_q.tasks import schedule
from django_q.models import Schedule


'''@shared_task
def add(x, y):
    print "in task"
    print "Start : %s" % time.ctime()
    time.sleep( 10 )
    print "End : %s" % time.ctime()
    return x + y'''
@task(bind=True)#name="error_handling"
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    print result
    print('Task {0} raised exception: {1!r}\n{2!r}'.format(
          uuid, result.result, result.traceback))

#@celery.decorators.periodic_task(run_every=timedelta(seconds=5))
@task()
def testing_task():
    print "IN TESTING TASK"
    return True

@task()#name="sum_two_numbers"
def add(x, y):
    print "in task"
    print "Start : %s" % time.ctime()
    time.sleep( 2 )
    print "End : %s" % time.ctime()
    #raise error_handler
    #raise Reject("201")

    raise Terminated
    #raise serializers.ValidationError({"oops":"Please update your app"})

    return x + y

@task()
def generateInvoiceItem():
    logger.info("task generateInvoiceItem")
    from api.models import *
    from api.v0.serializers import *

    todayDate = date.today()

    currentMonthStartDate = todayDate.replace(day=1)

    lastMonthEndDate = currentMonthStartDate - timedelta(days=1)
    lastMonthStartDate = lastMonthEndDate.replace(day=1)

    invoiceitem_company_ids = WishbookInvoiceItem.objects.filter(start_date=lastMonthStartDate, end_date=lastMonthEndDate, item_type='Share').values_list('company', flat=True)
    logger.info(str(invoiceitem_company_ids))

    companyObjs = Company.objects.all().exclude(id__in=invoiceitem_company_ids).order_by('id')
    for companyObj in companyObjs:
        invoice_ser = WishbookInvoiceItemSerializer(data={'company':companyObj.id, 'start_date':lastMonthStartDate, 'end_date':lastMonthEndDate, 'item_type':'Share'})
        if invoice_ser.is_valid():
            logger.info(str(companyObj.id))
            invoice_ser.save()
        else:
            logger.info(str(invoice_ser.errors))

    return True

@task()
def generateInvoice(company_ids, email_on_err=False):
    logger.info(str("task generateInvoice"))
    from api.models import *
    from api.v0.serializers import *

    todayDate = date.today()

    currentMonthStartDate = todayDate.replace(day=1)

    lastMonthEndDate = currentMonthStartDate - timedelta(days=1)
    lastMonthStartDate = lastMonthEndDate.replace(day=1)

    companies = Company.objects.filter(id__in=company_ids)
    for company in companies:
        logger.info(str(company.id))
        '''invoiceitems = InvoiceItem.objects.filter(company=company.id, start_date__gte=lastMonthStartDate, end_date__lte=lastMonthEndDate)

        billed_amount = 0
        for invoiceitem in invoiceitems:
            billed_amount += invoiceitem.amount
        '''
        invoice = WishbookInvoice.objects.filter(company=company, start_date=lastMonthStartDate, end_date=lastMonthEndDate).first()
        if invoice:
            invoice_ser = WishbookInvoiceSerializer(invoice, data={}, partial=True)
            if invoice_ser.is_valid():
                invoice_ser.save()
            else:
                logger.info(str(invoice_ser.errors))
        else:
            invoice_ser = WishbookInvoiceSerializer(data={'company':company.id, 'start_date':lastMonthStartDate, 'end_date':lastMonthEndDate})
            if invoice_ser.is_valid():
                invoice_ser.save()
            else:
                logger.info(str(invoice_ser.errors))
    return True

@task()
def generateCredit(company_ids, amount, expire_date):
    logger.info(str("task generateCredit"))
    from api.models import *

    companies = Company.objects.filter(id__in=company_ids)
    for company in companies:
        WishbookCredit.objects.create(company=company, amount=amount, balance_amount=amount, expire_date=expire_date)


@task()
def chatSend(url, headers, method=None, data=None, extra=None, action_name=""):
    logger.info("in chatSend applozic task - post or get ")
    #logger.info(str(data))
    if method == 'get':
        r = requests.get(url, data=data, headers=headers)
    else:
        r = requests.post(url, data=data, headers=headers)
    logger.info("for %s , %s json = %s , and response = %s" % (str(action_name), str(method), str(data), str(r.text)))

    '''logger.info(action_name)
    logger.info(str(data))
    logger.info(str(r))
    logger.info(str(r.text))'''
    if extra is not None:
        from api.models import *
        if extra['task'] == 'create_segmentation':
            segments=BuyerSegmentation.objects.filter(company=extra['company'], applozic_id__isnull=True)
            data = json.loads(data)
            userId = data['userId']
            url = 'group/v2/create?ofUserId='+userId
            for segment in segments:
                group_type = segment.group_type.values_list('id', flat=True)
                if segment.city.count() == 0:
                    city = City.objects.all().values_list('id', flat=True)
                else:
                    city = segment.city.values_list('id', flat=True)
                if segment.category.count() == 0:
                    category = Category.objects.all().values_list('id', flat=True)
                else:
                    category = segment.category.values_list('id', flat=True)

                #usrnames = Buyer.objects.filter(selling_company=segment.company, status="approved", group_type__in=group_type, buying_company__city__in=city, buying_company__category__in=category).values_list('buying_company__chat_admin_user__username', flat=True)
                usrnames = Buyer.objects.filter(Q(selling_company=segment.company, status="approved", group_type__in=group_type, buying_company__category__in=category) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).values_list('buying_company__chat_admin_user__username', flat=True)
                usrnames = list(usrnames)

                jsonarr = {"ofUserId":userId, "groupName":userId+" "+segment.segmentation_name, "groupMemberList":usrnames, "type":"5"}
                r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
                r = r.json()
                logger.info(str(r))
                segment.applozic_id = r["response"]["id"]
                segment.save()

        elif extra['task'] == 'set_segmentation_applozic_id':
            segment = BuyerSegmentation.objects.get(pk=extra['segmentation'])
            r = r.json()
            segment.applozic_id = r["response"]["id"]
            segment.save()

    return True


@task()
def facebookMessagerSend(full_phone_number, message):
    import json
    logger.info("in facebookMessagerSend task")
    url = "https://graph.facebook.com/v2.6/me/messages?access_token="+settings.FACEBOOK_MESSAGE_ACCESS_TOKEN
    headers = {'Content-Type': 'application/json'}
    #"+919925024856"
    data = {
        "messaging_type": "RESPONSE",
        "recipient":{
          "phone_number":full_phone_number
        },
        "message":{
          "text":message
        }
    }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    logger.info("phone_number = %s, message = %s and response = %s" % (full_phone_number, message, str(r.text)))

    return True

from api.common_functions import smsUrl, smsTrasaction
@task()
def smsSendSendSmart(mobile_nos, message, email_on_err=False):
    from api.models import *
    logger.info(str("task smsSendSendSmart"))

    template = urllib.quote_plus(message)

    reqs = []

    logger.info(str(template))

    for number in mobile_nos:
        url = smsUrl()% (number)
        url = url+template
        logger.info(str(url))
        res = grequests.get(url)
        reqs.append(res)
    greqs = grequests.map(reqs)
    logger.info(str(greqs))

    sent = 0
    i = 0
    for sendsmart in greqs:
        #print json.dumps(sendsmart)
        #print json.loads(sendsmart)
        if sendsmart.text == "Sent.":
            sent += 1
        elif email_on_err:
            mail_status = send_mail("SMS sendsmart", "Error = "+str(sendsmart.text)+" & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
            logger.info(str(mail_status))
            SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="sendsmart", error_text=str(sendsmart.text))
        i += 1

    smsTrasaction("sendsmart", sent)

    return True


#from api.common_functions import smsUrl, smsTrasaction
@task()
def smsSendTextNation(mobile_nos, message, email_on_err=False, send_without_queue=False):
    logger.info("task smsSendTextNation start")

    #temp_not_to_send_sms = ['+910000000001']
    #mobile_nos = list(set(mobile_nos) - set(temp_not_to_send_sms))
    #print "mobile_nos = ",mobile_nos

    if send_without_queue == False:
        logger.info("task smsSendTextNation checking queue shedule time")
        from api.common_functions import isScheduledTime, getScheduledTime
        from django.conf import settings
        if settings.TASK_QUEUE_METHOD == 'djangoQ':
            if isScheduledTime():
                logger.info("task smsSendTextNation set in schedule")
                from django_q.brokers import get_broker
                # set up a broker instance for better performance
                priority_broker = get_broker('priority')

                schedule('api.tasks.smsSendTextNation',
                    mobile_nos, message, email_on_err, send_without_queue,
                    schedule_type=Schedule.ONCE,
                    next_run=getScheduledTime(),
                    q_options={'broker': priority_broker}
                )
                return True

    from api.models import SmsError
    import math
    import time

    #return True
    template = urllib.quote_plus(message)

    logger.info("smsSendTextNation template = %s" % (template))

    divider = 25
    total_len = len(mobile_nos)
    looptimes = int(math.ceil(total_len / float(divider)))

    logger.info("smsSendTextNation total_len = %s, divider = %s, looptimes = %s" % (total_len, divider, looptimes))

    i = 0

    for lp in range(looptimes):
        loop_mobile_nos = mobile_nos[(lp*divider) : ((lp+1)*divider)]

        logger.info("smsSendTextNation lp = %s, loop_mobile_nos = %s" % (lp, loop_mobile_nos))

        reqs = []

        for number in loop_mobile_nos:
            url = "http://textnation.textnation.in/api/v3/index.php?method=sms&api_key=A9f3fd68a674f9d673201688e4d51050f&sender=WISHBK&format=json&to=%s&message="% (number)
            url = url+template
            #logger.info(str(url))
            res = grequests.get(url)
            reqs.append(res)

        greqs = grequests.map(reqs)

        logger.info("smsSendTextNation lp = %s, greqs len = %s, greqs response = %s" % (lp, len(greqs), greqs))

        sent = 0
        for sendsmart in greqs:
            if sendsmart is not None:
                sendsmart = sendsmart.json()

                #logger.info("smsSendTextNation sent sms response json = %s" % (sendsmart))

                if sendsmart['status'] == "OK":
                    sent += 1
                elif email_on_err:
                    mail_status = send_mail("SMS textnation", "Error = "+str(sendsmart['message'])+" & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
                    logger.info("smsSendTextNation lp = %s, status!=OK mail_status = %s" % (lp, mail_status))
                    SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="textnation", error_text=str(sendsmart['message']))
            else:
                mail_status = send_mail("SMS textnation", "Error = None & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
                logger.info("smsSendTextNation lp = %s, is None mail_status = %s" % (lp, mail_status))
                SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="textnation", error_text="")
            i += 1

        logger.info("smsSendTextNation lp = %s, sent successfully = %s, i (for mobile_nos[i]) = %s" % (lp, sent, i))

        smsTrasaction("textnation", sent)

        if len(loop_mobile_nos) == divider:
            time.sleep(1) #in second

    logger.info("task smsSendTextNation end")

    return True

@task()
def smsSendTextNationPromotional(mobile_nos, message, email_on_err=False):
    logger.info("task smsSendTextNationPromotional start")

    if settings.TASK_QUEUE_METHOD == 'djangoQ':
        logger.info("task smsSendTextNationPromotional checking queue shedule time")
        from api.common_functions import isScheduledTime, getScheduledTime
        if isScheduledTime():
            logger.info("task smsSendTextNationPromotional set in schedule")
            from django_q.brokers import get_broker
            # set up a broker instance for better performance
            priority_broker = get_broker('priority')

            schedule('api.tasks.smsSendTextNationPromotional',
                mobile_nos, message, email_on_err,
                schedule_type=Schedule.ONCE,
                next_run=getScheduledTime(),
                q_options={'broker': priority_broker}
            )
            return True

    from api.models import SmsError
    import math
    import time

    template = urllib.quote_plus(message)

    logger.info("smsSendTextNationPromotional template = %s" % (template))

    if settings.DEBUG:
        logger.info("NOT sending SMS if settings.DEBUG=True")
        return True #for local development

    divider = 25
    total_len = len(mobile_nos)
    looptimes = int(math.ceil(total_len / float(divider)))

    logger.info("smsSendTextNationPromotional total_len = %s, divider = %s, looptimes = %s" % (total_len, divider, looptimes))

    i = 0

    for lp in range(looptimes):
        loop_mobile_nos = mobile_nos[(lp*divider) : ((lp+1)*divider)]

        logger.info("smsSendTextNationPromotional lp = %s, loop_mobile_nos = %s" % (lp, loop_mobile_nos))

        reqs = []

        for number in loop_mobile_nos:
            url = "http://textnation.textnation.in/api/v4/?method=sms&api_key=A9cd320eee926814c622d12692daeb570&sender=WISHBK&format=json&to=%s&message="% (number)
            url = url+template
            #logger.info(str(url))
            res = grequests.get(url)
            reqs.append(res)

        greqs = grequests.map(reqs)

        logger.info("smsSendTextNationPromotional lp = %s, greqs len = %s, greqs response = %s" % (lp, len(greqs), greqs))

        sent = 0
        for sendsmart in greqs:
            if sendsmart is not None:
                sendsmart = sendsmart.json()

                #logger.info("smsSendTextNationPromotional sendsmart = %s" % (sendsmart))

                if sendsmart['status'] == "OK":
                    sent += 1
                elif email_on_err:
                    mail_status = send_mail("SMS textnation Promotional", "Error = "+str(sendsmart['message'])+" & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
                    logger.info("smsSendTextNationPromotional lp = %s, status!=OK mail_status = %s" % (lp, mail_status))
                    SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="textnation_promotional", error_text=str(sendsmart['message']))
            else:
                mail_status = send_mail("SMS textnation Promotional", "Error = None & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
                logger.info("smsSendTextNationPromotional lp = %s, is None mail_status = %s" % (lp, mail_status))
                SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="textnation", error_text="")
            i += 1

        logger.info("smsSendTextNationPromotional lp = %s, sent successfully = %s, i (for mobile_nos[i]) = %s" % (lp, sent, i))

        smsTrasaction("textnation_promotional", sent)

        if len(loop_mobile_nos) == divider:
            time.sleep(1) #in second

    logger.info("task smsSendTextNationPromotional end")

    return True

@task()
def smsSendICubes(mobile_nos, message, email_on_err=False):
    from api.models import *
    logger.info("task smsSendICubes")
    template = urllib.quote_plus(message)

    logger.info(str(template))

    SMS_URL = 'https://v1.iproapi.com/api/sms/sendotp'
    SMS_MESSAGETYPE = 'trans'
    SMS_HEADER = [
        'Content-type: Application/json',
        'X-Token: PND9MhSwqgTcKOQwIgzVq9g+Hevy1+e07z+O2MvIo/0ZclBzhhZT5IWjV4GFL+ximGBb4bOvWHtHsJS1/g/3P8nr7x/naRkKxhFvMGzvdV2JCMu1Ifw14ACZT/bplEZ4yPdvexvC3fe/vwm+LUmxY1cnWrsoS5dKsO1/6IDBsVqowWl5vsi2xiFX2tm9y2Ner8ZvLuqL1h4CeergUshb55y1dbVapG1FD3b9Rpcf0jOsuU9Hmm8cQZ4FvVm9QT+qZbmeA4SVJfFxW43UyybwTDjqgKEMdFYGLQuTbu5SrMqmxsjzmNfW5Ir8tC/J+4DZjTCZM118ASsW9Y1lsCpBNQ=='
    ]

    reqs = []
    m = pycurl.CurlMulti()
    #print "before for"
    for mobile_no in mobile_nos:
        response = StringIO()
        handle = pycurl.Curl()
        handle.setopt(pycurl.URL, SMS_URL)
        handle.setopt(pycurl.HTTPHEADER, SMS_HEADER)
        handle.setopt(pycurl.POST, 1)

        data = json.dumps({"Mobile":mobile_no,"Message":template,"MessageType":SMS_MESSAGETYPE,"TriggerSMSid":"177","Listid":"228"})

        handle.setopt(pycurl.POSTFIELDS, data)

        handle.setopt(pycurl.WRITEFUNCTION, response.write)
        req = (SMS_URL, response, handle)
        # Note that the handle must be added to the multi object
        # by reference to the req tuple (threading?).
        m.add_handle(req[2])
        reqs.append(req)
    #print "after for"
    SELECT_TIMEOUT = 1.0
    num_handles = len(reqs)
    #print "before while"
    while num_handles:
        ret = m.select(SELECT_TIMEOUT)
        if ret == -1:
            continue
        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
    #print "after while"

    logger.info(str(reqs))

    sent = 0
    i = 0
    for req in reqs:
        try:
            revalue = req[1].getvalue()# contains response content
            logger.info("revalue === ")
            logger.info(str(revalue))

            if str(revalue) == "":
                mail_status = send_mail("SMS icubes", "Error = "+str(revalue)+" & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
                logger.info(str(mail_status))
                SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="icubes", error_text=str(revalue))
                continue

            revalue = json.loads(revalue)
            #print "revalue in json === "
            #print revalue
            if revalue['Success']:
                sent += 1
            elif email_on_err:
                mail_status = send_mail("SMS icubes", "Error = "+str(revalue)+" & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
                logger.info(str(mail_status))
                SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="icubes", error_text=str(revalue))
        except Exception as e:
            logger.info("icubes Exception = ")
            logger.info(str(e))
            mail_status = send_mail("SMS icubes", "Error = "+str(revalue)+" & mobile no = "+str(mobile_nos[i])+" & template = "+template, "tech@wishbook.io", ["tech@wishbook.io"])
            logger.info("Exception mail_status=")
            logger.info(str(mail_status))
            SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="icubes", error_text=str(revalue))
        i += 1

    smsTrasaction("icubes", sent)

    return True

@task()
def notificationSend(userids, message, exjson, notification_type=None):
    logger.info("In notificationSend task")
    from api.common_functions import isScheduledTime, getScheduledTime
    from django.conf import settings
    if settings.TASK_QUEUE_METHOD == 'djangoQ':
        if isScheduledTime():
            from django_q.brokers import get_broker
            # set up a broker instance for better performance
            priority_broker = get_broker('priority')

            schedule('api.tasks.notificationSend',
                userids, message, exjson, notification_type,
                schedule_type=Schedule.ONCE,
                next_run=getScheduledTime(),
                q_options={'broker': priority_broker}
            )
            return True

    from push_notifications.models import GCMDevice ,APNSDevice
    from api.models import *
    from django.contrib.auth.models import User

    if notification_type == 'gcm':
        try:
            logger.info("notificationSend gcm")
            device = GCMDevice.objects.filter(user__in=userids, active=True).order_by('-id')
            logger.info("notificationSend gcm device = %s, message = %s, exjson = %s, userids = %s"% (str(device), str(message), str(exjson), str(userids)))
            '''logger.info(str(userids))
            logger.info(str(message))
            logger.info(str(exjson))
            logger.info(str(device))'''
            status = device.send_message(message, extra=exjson)
            logger.info("gcm send status = %s"% (str(status)))
            #logger.info(str(status))
        except Exception as e:
            logger.info("In Exception")
            logger.info(str(e))
            mail_status = send_mail("Notification GCM", "Error = "+str(e)+" & message = "+str(message)+" & exjson = "+str(exjson), "tech@wishbook.io", ["tech@wishbook.io"])
            pass
    elif notification_type == 'apns':
        try:
            logger.info("notificationSend apns")
            device = APNSDevice.objects.filter(user__in=userids, active=True).order_by('-id')
            logger.info("notificationSend apns device = %s, message = %s, exjson = %s, userids = %s"% (str(device), str(message), str(exjson), str(userids)))
            '''logger.info(str(userids))
            logger.info(str(message))
            logger.info(str(exjson))
            logger.info(str(device))'''
            status = device.send_message(message, extra=exjson)
            logger.info("apns send status = %s"% (str(status)))
            #logger.info(str(status))
        except Exception as e:
            logger.info("In Exception")
            logger.info(str(e))
            mail_status = send_mail("Notification APNS", "Error = "+str(e)+" & message = "+str(message)+" & exjson = "+str(exjson), "tech@wishbook.io", ["tech@wishbook.io"])
            pass
    else:
        logger.info("notificationSend both")
        try:
            device = GCMDevice.objects.filter(user__in=userids, active=True).order_by('-id')
            logger.info("notificationSend gcm device = %s, message = %s, exjson = %s, userids = %s"% (str(device), str(message), str(exjson), str(userids)))
            '''logger.info(str(userids))
            logger.info(str(message))
            logger.info(str(exjson))
            logger.info(str(device))'''
            status = device.send_message(message, extra=exjson)
            logger.info("gcm send status = %s"% (str(status)))
            #logger.info("gcm=")
            #logger.info(str(status))
        except Exception as e:
            logger.info("In Exception")
            logger.info(str(e))
            mail_status = send_mail("Notification GCM", "Error = "+str(e)+" & message = "+str(message)+" & exjson = "+str(exjson), "tech@wishbook.io", ["tech@wishbook.io"])
            pass

        try:
            device = APNSDevice.objects.filter(user__in=userids, active=True).order_by('-id')
            logger.info("notificationSend apns device = %s, message = %s, exjson = %s, userids = %s"% (str(device), str(message), str(exjson), str(userids)))
            '''logger.info(str(userids))
            logger.info(str(message))
            logger.info(str(exjson))
            logger.info(str(device))'''
            status = device.send_message(message, extra=exjson)
            logger.info("apns send status = %s"% (str(status)))
            #logger.info("apns=")
            #logger.info(str(status))
        except Exception as e:
            logger.info("In Exception")
            logger.info(str(e))
            mail_status = send_mail("Notification APNS", "Error = "+str(e)+" & message = "+str(message)+" & exjson = "+str(exjson), "tech@wishbook.io", ["tech@wishbook.io"])
            pass

    try:
        if "push_id" in exjson:
            logger.info("has push_id")
            users = User.objects.filter(id__in=userids)
            for user in users:
                usnObj, created = UserSendNotification.objects.get_or_create(user=user, created_at=date.today())
                usnObj.send_gcm = usnObj.send_gcm + 1
                usnObj.save()

    except Exception as e:
        logger.info("In Exception")
        logger.info("in notificationSend task push_id error")
        logger.info(str(e))
        pass

    return True

@task()
def emailSend(subject, message, from_email, to_email, html_message):
    logger.info("emailSend task")
    mail_status = send_mail(subject, message, from_email, to_email, html_message=html_message)
    logger.info(mail_status)

    return True



'''
@task()
def chat_user_registration(jsonarr):
    url = 'register/client'
    r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
    print r
    print r.text

    return r.text
'''

@task()
def dfsPushTask(buyers, completedBuyers, pushDownstream, pushObj, pushType, pushImage, title, city, category, catalogs, selections, catalogProducts, selectionProducts, catalogRate, selectionRate, pushName, group_type, sellingCompany, fullCatalogOrders, companyImage, tableId, sendSMS, getObj): #supplier,
    logger.info("== dfsPushTask() ==")
    logger.info("In dfsPushTask start at "+str(datetime.now()))

    from api.models import *
    from api.v1.serializers import *
    from decimal import Decimal

    if getObj:
        buyers = Buyer.objects.filter(id__in=buyers)
        pushObj = Push.objects.get(pk=pushObj)
        catalogs = Catalog.objects.filter(id__in=catalogs)
        selections = Selection.objects.filter(id__in=selections)
        sellingCompany = Company.objects.get(pk=sellingCompany)


    #global push_users
    #global peding_push_users
    #global dfsCount

    #global push_user_product
    #global push_user


    logger.info("all buyers = ")


    #logger.info(buyers)

    for buyer in buyers:
        logger.info("buyer obj=")

        completedBuyers = Push_User.objects.filter(push=pushObj).values_list('buying_company', flat=True)
        completedBuyers = list(completedBuyers)

        #logger.info(buyer)
        #print completedBuyers
        ###if buyer not in completedBuyers:
        if buyer.buying_company.id not in completedBuyers:
            logger.info("Buyer===>>")
            logger.info(buyer.buying_company.name)

            pusers = []
            companyUsers = CompanyUser.objects.filter(company=buyer.buying_company, user__groups__name="administrator").select_related('user','company')#.values_list('user', flat=True).distinct()

            for companyUser in companyUsers:
                logger.info("User==>")
                #logger.info(companyUser.user.username)
                #print companyUser.id
                #logger.info(companyUser)

                #logger.info(catalogs)
                #logger.info(selections)
                index=0

                push_user_product = []#list()#


                for catalog in catalogs:
                    #print catalog
                    totalPrice = 0
                    sellingPrice = 0
                    rate = catalogRate[index]
                    fixRate = rate[0]
                    percentageRate = rate[1]
                    for product in catalogProducts[index]:
                        #print product
                        productObj=Product.objects.get(pk=product[0])

                        price = Decimal(product[2]) + (Decimal(product[2])*Decimal(percentageRate)/100) + Decimal(fixRate) ######### , supplier, fixRate, percentageRate
                        #logger.info(">>>>product>>>>")
                        #logger.info(product)
                        #logger.info(">>>>price>>>>")
                        #logger.info(price)
                        totalPrice = totalPrice+price
                        sellingPrice=sellingPrice+product[2]
                        #productUserObj = Push_User_Product.objects.create(push=pushObj, user=companyUser.user, product=productObj, price=price, sku=product[1], catalog=catalog, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=product[2])
                        push_user_product.append(Push_User_Product(push=pushObj, user=companyUser.user, product=productObj, price=price, sku=product[1], catalog=catalog, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=product[2]))

                        cpfObj = CompanyProductFlat.objects.filter(product=productObj, catalog=catalog, buying_company=companyUser.company).last()
                        if cpfObj:#CompanyProductFlat.objects.filter(product=productObj, catalog=catalog, buying_company=companyUser.company).exists():

                            if cpfObj.final_price > price or cpfObj.selling_company == sellingCompany:
                                sellPrice = (price+buyer.fix_amount) + ((price*buyer.percentage_amount)/100)
                                cpfObj.final_price = price
                                cpfObj.selling_price = sellPrice
                                cpfObj.selling_company = sellingCompany
                                cpfObj.push_reference = pushObj
                                cpfObj.save()
                        else:
                            sellPrice = (price+buyer.fix_amount) + ((price*buyer.percentage_amount)/100)
                            CompanyProductFlat.objects.create(product=productObj, catalog=catalog, buying_company=companyUser.company, final_price=price, selling_price=sellPrice, selling_company=sellingCompany, push_reference=pushObj)
                    #logger.info("#########>>>>totalPrice>>>>")
                    #logger.info(totalPrice)
                    pushuser = Push_User.objects.create(push=pushObj, user=companyUser.user, catalog=catalog, total_price=totalPrice, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=sellingPrice, full_catalog_orders_only=fullCatalogOrders)
                    ###push_user.append(Push_User(push=pushObj, user=companyUser.user, catalog=catalog, total_price=totalPrice, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=sellingPrice, full_catalog_orders_only=fullCatalogOrders))
                    index+=1
                index=0
                for selection in selections:
                    totalPrice = 0
                    sellingPrice = 0
                    rate = selectionRate[index]
                    fixRate = rate[0]
                    percentageRate = rate[1]
                    for product in selectionProducts[index]:
                        productObj=Product.objects.get(pk=product[0])

                        price = Decimal(product[2]) + (Decimal(product[2])*Decimal(percentageRate)/100) + Decimal(fixRate) ######### , supplier, fixRate, percentageRate
                        #logger.info(">>>>product>>>>")
                        #logger.info(product)
                        #logger.info(">>>>price>>>>")
                        #logger.info(price)
                        totalPrice = totalPrice+price
                        sellingPrice=sellingPrice+product[2]
                        #productUserObj = Push_User_Product.objects.create(push=pushObj, user=companyUser.user, product=productObj, price=price, sku=product[1], selection=selection, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=product[2])
                        push_user_product.append(Push_User_Product(push=pushObj, user=companyUser.user, product=productObj, price=price, sku=product[1], selection=selection, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=product[2]))

                        cpfObj = CompanyProductFlat.objects.filter(product=productObj, selection=selection, buying_company=companyUser.company).last()
                        if cpfObj:#CompanyProductFlat.objects.filter(product=productObj, selection=selection, buying_company=companyUser.company).exists():

                            if cpfObj.final_price > price or cpfObj.selling_company == sellingCompany:
                                sellPrice = (price+buyer.fix_amount) + ((price*buyer.percentage_amount)/100)
                                cpfObj.final_price = price
                                cpfObj.selling_price = sellPrice
                                cpfObj.selling_company = sellingCompany
                                cpfObj.push_reference = pushObj
                                cpfObj.save()
                        else:
                            sellPrice = (price+buyer.fix_amount) + ((price*buyer.percentage_amount)/100)
                            CompanyProductFlat.objects.create(product=productObj, selection=selection, buying_company=companyUser.company, final_price=price, selling_price=sellPrice, selling_company=sellingCompany, push_reference=pushObj)
                    #logger.info("#########>>>>totalPrice>>>>")
                    #logger.info(totalPrice)
                    pushuser = Push_User.objects.create(push=pushObj, user=companyUser.user, selection=selection, total_price=totalPrice, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=sellingPrice, full_catalog_orders_only=fullCatalogOrders)
                    ###push_user.append(Push_User(push=pushObj, user=companyUser.user, selection=selection, total_price=totalPrice, selling_company=sellingCompany, buying_company=companyUser.company, selling_price=sellingPrice, full_catalog_orders_only=fullCatalogOrders))
                    index+=1

                #=====#
                #push(companyUser.user, title, pushObj.id, pushType, pushImage, pushName)
                #push_users.append(companyUser.user)

                Push_User_Product.objects.bulk_create(push_user_product)
                pusers.append(companyUser.user)
                #logger.info("pushed to companyuser"+str(companyUser.user.username))
            #completedBuyers.append(buyer.buying_company.id)
            push(pusers, title, pushObj.id, pushType, pushImage, pushName, companyImage, tableId, sendSMS, buyer.buying_company)
            #logger.info("Buyer id===>>")
            #logger.info(buyer.buying_company.id)
            #logger.info("completedBuyers===>>")
            #logger.info(completedBuyers)

            if pushDownstream=="yes" and buyer.buying_company.push_downstream=="yes":
                logger.info("<<<<<<<<<push_downstream==yes from")
                #logger.info(buyer.buying_company.name)
                if  buyer.buying_company.id not in completedBuyers:
                    #completedBuyers.append(buyer.buying_company.id)


                    disableProducts = True
                    if catalogs:
                        #disableProducts = Push_User_Product.all_objects.filter(selling_company=buyer.buying_company, catalog=catalogs[0], deleted=True).exists()  #values_list('product', flat=True)
                        disableProducts = CatalogSelectionStatus.objects.filter(company=buyer.buying_company, catalog=catalogs[0], status="Disable").exists()  #values_list('product', flat=True)
                    elif selections:
                        #disableProducts = Push_User_Product.all_objects.filter(selling_company=buyer.buying_company, selection=selections[0], deleted=True).exists()  #values_list('product', flat=True)
                        disableProducts = CatalogSelectionStatus.objects.filter(company=buyer.buying_company, selection=selections[0], status="Disable").exists()

                    if disableProducts:
                        continue

                    #subBuyers = Buyer.objects.filter(selling_company = buyer.buying_company, status='approved', buying_company__city__in=city, buying_company__category__in=category).distinct().select_related('selling_company', 'buying_company') #.values_list('buying_company', flat=True).distinct()  #, group_type__in=group_type
                    subBuyers = Buyer.objects.filter(Q(selling_company = buyer.buying_company, status='approved', buying_company__category__in=category) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company') #.values_list('buying_company', flat=True).distinct()  #, group_type__in=group_type

                    '''if pushobj.buyer_segmentation.segmentation_name == "Send All":
                        phone_numbers = Buyer.objects.filter(selling_company = buyer.buying_company, status__in=['buyer_pending','supplier_pending'], buying_company__city__in=city, buying_company__category__in=category, group_type__in=group_type).values_list('buying_company__phone_number', flat=True).distinct()
                        invitee_numbers = Buyer.objects.filter(selling_company = buyer.buying_company, status__in=['buyer_registrationpending','supplier_registrationpending'], group_type__in=group_type).values_list('invitee__invitee_number', flat=True).distinct()
                        print phone_numbers
                        print invitee_numbers
                        peding_push_users.extend(phone_numbers)
                        peding_push_users.extend(invitee_numbers)
                        print peding_push_users'''

                    logger.info("subBuyers=")
                    #logger.info(subBuyers)
                    if subBuyers:# and buyer.buying_company.id not in completedBuyers:
                        logger.info(">>>HAS SUB BUYERS")
                        #buyerUser = CompanyUser.objects.filter(company=buyer.buying_company, user__groups__name="administrator").first()

                        ##newPushobj = Push.objects.create(push_downstream=pushObj.push_downstream,message=pushObj.message,buyer_segmentation=pushObj.buyer_segmentation, company=buyer.buying_company,user=buyerUser.user, to_show="no")
                        #logger.info(buyerUser)

                        newCatalogRate = []
                        newSelectionRate = []
                        buyerRateobj = Buyer.objects.filter(selling_company=buyer.selling_company, buying_company=buyer.buying_company, status="approved").last()
                        famt = buyerRateobj.fix_amount
                        pamt = buyerRateobj.percentage_amount
                        for crate in catalogRate:
                            newCatalogRate.append([Decimal(crate[0])+famt, (Decimal(crate[1])+pamt)+(pamt*Decimal(crate[1]/100))])
                        for srate in selectionRate:
                            newSelectionRate.append([Decimal(srate[0])+famt, (Decimal(srate[1])+pamt)+(pamt*Decimal(srate[1]/100))])

                        logger.info("======NEW RATE======")
                        #logger.info(newCatalogRate)
                        #logger.info(newSelectionRate)
                        logger.info("dfsPush Recursion call")

                        #dfsPush(subBuyers, completedBuyers, pushDownstream, pushObj, pushType, pushImage, title, city, category, catalogs, selections, catalogProducts, selectionProducts, newCatalogRate, newSelectionRate, pushName, group_type, buyer.buying_company, fullCatalogOrders, companyImage, tableId, sendSMS) #supplier,

                        logger.info("applozic pushserializer msg")
                        ofUserId = buyer.buying_company.chat_admin_user
                        ofUserId = str(ofUserId)
                        nbs = BuyerSegmentation.objects.filter(segmentation_name=pushObj.buyer_segmentation.segmentation_name, company=buyer.buying_company).first()
                        if nbs:
                            #logger.info("nbs")
                            for catalog in catalogs:
                                brandName = catalog.brand.name
                                #message = '%s has shared you a new %s %s' % (brandName, pushType, title)
                                message = '%s has shared you a new %s' % (brandName, title)
                                r = chat_send_message({"ofUserId":ofUserId, "groupId":str(nbs.applozic_id), "message":message})
                                #logger.info("nbs catalog")
                            for selection in selections:
                                brandName=selectionObj.user.companyuser.company.name
                                #message = '%s has shared you a new %s %s' % (brandName, pushType, title)
                                message = '%s has shared you a new %s' % (brandName, title)
                                r = chat_send_message({"ofUserId":ofUserId, "groupId":str(nbs.applozic_id), "message":message})
                                #logger.info("nbs selection")
                        logger.info("applozic pushserializer msg end")


                        subBuyers = subBuyers.values_list('id', flat=True)
                        subBuyers = list(subBuyers)
                        catalogs1 = []
                        selections1 = []
                        if catalogs:
                            catalogs1 = catalogs.values_list('id', flat=True)
                            #catalogs = list(catalogs)
                        else:
                            selections1 = selections.values_list('id', flat=True)
                            #selections = list(selections)
                        catalogs1 = list(catalogs1)
                        selections1 = list(selections1)

                        if settings.TASK_QUEUE_METHOD == 'celery':
                            dfsPushTask.apply_async((subBuyers, completedBuyers, pushDownstream, pushObj.id, pushType, pushImage, title, city, category, catalogs1, selections1, catalogProducts, selectionProducts, newCatalogRate, newSelectionRate, pushName, group_type, buyer.buying_company.id, fullCatalogOrders, companyImage, tableId, sendSMS, True), expires=datetime.now() + timedelta(days=2))
                        elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                            task_id = async(
                                'api.tasks.dfsPushTask',  # func full name
                                subBuyers, completedBuyers, pushDownstream, pushObj.id, pushType, pushImage, title, city, category, catalogs1, selections1, catalogProducts, selectionProducts, newCatalogRate, newSelectionRate, pushName, group_type, buyer.buying_company.id, fullCatalogOrders, companyImage, tableId, sendSMS, True
                            )
        else:
            logger.info("********************/////////allready shared/////////***************")
    #push(push_users, title, pushObj.id, pushType, pushImage, pushName)
    logger.info("In dfsPush end at "+str(datetime.now()))
    return

@task()
def dailyShareSMS():
    from datetime import date, datetime, timedelta
    from api.models import *
    from django.db.models.functions import Concat
    import random

    logger.info("in dailyShareSMS")
    #todayDate = date.today()
    oldChObj = CronHistory.objects.filter(cron_type="dailyShareSMS").order_by('-time').first()
    if oldChObj:
        lastDate = oldChObj.time
    else:
        lastDate = datetime.now() - timedelta(days=1)
    #lastDate = datetime.now() - timedelta(days=100) #local use porpose
    logger.info(str(lastDate))

    todayDate = datetime.now()
    chObj = CronHistory.objects.create(cron_type="dailyShareSMS", time=todayDate)
    logger.info(str(todayDate))

    #buying_companies = Push_User.objects.filter(push__time__lte=todayDate, push__time__gte=lastDate, catalog__isnull=False).values_list('buying_company', flat=True).distinct().order_by('buying_company')

    unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

    purawqueryset = Push_User.objects.raw('SELECT `api_push_user`.`id`, `api_push_user`.`buying_company_id`, COUNT(`api_push_user`.`buying_company_id`) AS `buying_company_count`, COUNT(DISTINCT `api_push_user`.`catalog_id`) AS `catalog_count`, MAX(DISTINCT `api_push_user`.`catalog_id`) AS `catalog_id` FROM `api_push_user` INNER JOIN `api_push` ON ( `api_push_user`.`push_id` = `api_push`.`id` ) WHERE (`api_push_user`.`deleted` = False AND `api_push`.`time` >= "'+str(lastDate.strftime("%Y-%m-%d %H:%M:%S"))+'" AND `api_push`.`time` <= "'+str(todayDate.strftime("%Y-%m-%d %H:%M:%S"))+'" AND `api_push_user`.`catalog_id` IS NOT NULL) GROUP BY `api_push_user`.`buying_company_id` HAVING `buying_company_count` > 1 and `catalog_count` > 1')
    print purawqueryset
    print purawqueryset.query

    #for buying_company in buying_companies:
    for purawquery in purawqueryset:
        buying_company = purawquery.buying_company_id
        totalcatalogs = purawquery.catalog_count
        catalog_id = purawquery.catalog_id
        #print "catalog_id=",catalog_id

        logger.info("buying_company id == == %s"% (str(buying_company)))
        '''totalcatalogs = Push_User.objects.filter(push__time__lte=todayDate, push__time__gte=lastDate, buying_company=buying_company, catalog__isnull=False).values_list('catalog', flat=True).distinct().count()

        if totalcatalogs <= 1:
            logger.info("totalcatalogs <= 1: continue --")
            continue'''

        users = CompanyUser.objects.filter(company=buying_company, user__groups__name="administrator").values_list('user', flat=True).distinct()

        # rno = random.randrange(100000, 999999, 1)
        # message = "Aaj aapko "+str(totalcatalogs)+" naye catalog share kiye gaye"

        catalogObj = Catalog.objects.get(pk=catalog_id)
        image = catalogObj.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url

        # if settings.TASK_QUEUE_METHOD == 'celery':
        #     notificationSend.apply_async((users, message, {"notId": rno, "title":"Catalogs Received", "push_type":"catalog", "type":"catalog", "image":image, "other_para":{"ctype":"received"}}), expires=datetime.now() + timedelta(days=2))
        # elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        #     task_id = async(
        #         'api.tasks.notificationSend',
        #         users, message, {"notId": rno, "title":"Catalogs Received", "push_type":"catalog", "type":"catalog", "image":image, "other_para":{"ctype":"received"}}
        #     )

        users = User.objects.filter(id__in=users)

        # for userObj in users:
        #     if "+91" not in userObj.userprofile.country.phone_code:
		# 		continue
        #
        #     phone_number = UserProfile.objects.filter(user=userObj).annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()
        #     phone_number = list(set(phone_number) - set(unsubscribed_number))
        #     if len(phone_number) == 0:
        #         logger.info("phone_number == 0: continue --")
        #         continue
        #
        #     otp = None
        #     if userObj.userprofile.is_profile_set == False:
        #         logger.info("if userObj.userprofile.is_profile_set == False")
        #         otpObj = RegistrationOTP.objects.filter(phone_number=userObj.userprofile.phone_number, country=userObj.userprofile.country).order_by('-id').first()
        #         if otpObj:
        #             logger.info("if RegistrationOTP obj available")
        #             otp = otpObj.otp
        #     if otp is None:
        #         logger.info("if otp is None")
        #         otp = random.randrange(100000, 999999, 1)
        #         registrationOtp = RegistrationOTP.objects.create(phone_number=userObj.userprofile.phone_number, otp=otp, country=userObj.userprofile.country)
        #
        #     smsurl = 'https://app.wishbooks.io/?m='+str(userObj.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(userObj.userprofile.country.id)+'&t=page&id=received'
        #     smsurl = urlShortener(smsurl)
        #
        #     template = smsTemplates("daily_1_share_sms")% (totalcatalogs, smsurl)
        #     logger.info(str(template))
        #     #smsSend(phone_number, template)
        #     logger.info("in_queue smsSendTextNationPromotional")
        #     if settings.TASK_QUEUE_METHOD == 'celery':
        #         smsSendTextNationPromotional.apply_async((phone_number, template, True), expires=datetime.now() + timedelta(days=2))
        #     elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        #         task_id = async(
        #             'api.tasks.smsSendTextNationPromotional',
        #             phone_number, template, True
        #         )
        #
        #     usnObj, created = UserSendNotification.objects.get_or_create(user=userObj, created_at=date.today())
        #     usnObj.send_sms = usnObj.send_sms + 1
        #     usnObj.save()
        #     #sending sms here

        jsondata = {"image":image, "total_catalogs":totalcatalogs}
        sendAllTypesMessage("daily_1_share_sms", users, jsondata)

    #for public catalog upload buyer notification
    '''todayDate = date.today()
    comrawquerys = Catalog.objects.filter(view_permission="public", created_at=todayDate).values('company').annotate(company_count=Count('company')).filter(company_count__gt=1)
    for comrawquery in comrawquerys:
        print comrawquery

        company = Company.objects.get(pk=comrawquery['company'])

        rno = random.randrange(100000, 999999, 1)
        buyers = Buyer.objects.filter(selling_company=comrawquery['company'], status="approved").values_list('buying_company', flat=True)
        users = CompanyUser.objects.filter(company__in = buyers, user__groups__name="administrator").values_list('user', flat=True).distinct()
        users = list(users)
        message = company.name+" has added "+str(comrawquery['company_count'])+" catalogs"
        if settings.TASK_QUEUE_METHOD == 'celery':
            notificationSend.apply_async((users, message, {"notId":rno,"push_type":"catalog", "title":"Public Catalogs", "name":"Public Catalogs"}), expires=datetime.now() + timedelta(days=2))
        elif settings.TASK_QUEUE_METHOD == 'djangoQ':
            task_id = async(
                'api.tasks.notificationSend',
                users, message, {"notId":rno,"push_type":"catalog", "title":"Public Catalogs", "name":"Public Catalogs"}
            )'''


@task()
def buyerCSVImportJobs(job_id):
    logger.info("buyerCSVImportJobs task job_id = %s"% (job_id))
    from api.models import *
    from rest_framework.response import Response
    from django.http import HttpResponse
    from api.common_functions import add_buyer_v1, common_user_registration
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    #from api.v0.serializers import RegisterSerializer
    from api.v1.serializers import requestNotification
    from api.v1.views import randomString
    import random
    from django.utils import timezone

    logger.info("buyerCSVImportJobs task 1.1")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()
    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    logger.info("buyerCSVImportJobs task 1.2")

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    err = ""
    logger.info("buyerCSVImportJobs task 1.3")

    errorfilename = 'jobs_error_file/buyers_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    errorfile = open(errorfilepath, "wb+")
    writer = csv.writer(errorfile)

    logger.info("buyerCSVImportJobs task 1.4")

    fieldnames = ['country_code', 'buyer_number', 'buyer_name', 'group_type', 'state', 'city', 'gst', 'pan', 'error']
    writer.writerow(fieldnames)

    column = 1
    rows = 0
    last_buyer_name = None
    last_buyer_company_obj = None

    companyIds = []
    bulk_buyers = []

    errors_unique = []

    country_code = buyer_name = buyer_number = state = city = group_type_text = ""
    fields = {}

    logger.info("buyerCSVImportJobs task 1.5")

    wrong_csv_uploaded = False

    try:
        csv_headers = reader.fieldnames
        print "csv_headers = ",csv_headers

        for csv_header in csv_headers:
            if csv_header not in fieldnames:
                wrong_csv_uploaded = True
    except Exception as e:
        logger.info("buyerCSVImportJobs Exception = %s"% (e))
        mail_status = send_mail("buyerCSVImportJobs Exception", "Error = "+str(e), "tech@wishbook.io", ["tech@wishbook.io"])
        return False

    logger.info("buyerCSVImportJobs task 1.6")

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        try:
            for fields in reader:
                try:
                    column += 1
                    logger.info("json fields = %s"% (str(fields)))

                    buyer_name = fields['buyer_name']
                    buyer_number = fields['buyer_number']
                    state = fields.get('state', None)
                    city = fields.get('city', None)

                    group_type_text = fields['group_type']
                    country_code = fields['country_code']

                    gst = fields.get('gst', None)
                    pan = fields.get('pan', None)

                    if int(buyer_number[0]) in [0,1,2,3,4,5]:
                        logger.info("Mobile number is not valid")
                        err = {"buyer_csv":"Mobile number is not valid : "+str(buyer_number)}
                        writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, "Mobile number is not valid",])
                        continue

                    if not GroupType.objects.filter(name=fields['group_type']).exists():
                        logger.info("Enter a valid group type")
                        err = {"buyer_csv":"Enter a valid group type : "+fields['group_type']}
                        writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, "Enter a valid group type",])
                        continue

                    if not Country.objects.filter(phone_code="+"+country_code).exists():
                        logger.info("Enter a valid country code")
                        err = {"buyer_csv":"Enter a valid country code : "+fields['country_code']}
                        writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, "Enter a valid country code",])
                        continue

                    if not buyer_number.isdigit():
                        err = {"buyer_csv":"Enter a valid buyer number : "+buyer_number}
                        writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, "Enter a valid buyer number",])
                        continue

                    if gst:
                        if len(str(gst)) != 15:
                            logger.info("Enter a valid gst")
                            err = {"buyer_csv":"Enter a valid gst : "+str(gst)}
                            writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, "Enter a valid gst",])
                            continue

                    if pan:
                        if len(str(pan)) != 10:
                            logger.info("Enter a valid pan")
                            err = {"buyer_csv":"Enter a valid pan : "+str(pan)}
                            writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, "Enter a valid pan",])
                            continue

                    country = Country.objects.get(phone_code="+"+country_code)
                    group_type = GroupType.objects.filter(name=fields['group_type']).first()

                    #if last_buyer_name is not None and last_buyer_name != "" and last_buyer_name == buyer_name: #on removing bulk buyer
                    if last_buyer_name is not None and last_buyer_name != "" and last_buyer_name == buyer_name and last_buyer_company_obj is not None:
                        logger.info("buyerCSVImportJobs last_buyer_name is matched with buyer_name")
                        logger.info(str(last_buyer_company_obj))

                        compnumber = getCompanyNumberFromNumber(country, buyer_number)
                        country = compnumber[0]
                        buyer_number = compnumber[1]
                        if Company.objects.filter(country=country, phone_number=buyer_number).exists() or UserProfile.objects.filter(country=country, phone_number=buyer_number).exists():
                            continue

                        if state:
                            state = State.objects.filter(state_name=state).first()
                        if state is None or state == "":
                            state = State.objects.filter(state_name="-").first()

                        if city:
                            city = City.objects.filter(city_name=city).first() #, state=state
                        if city is None or city == "":
                            city = City.objects.filter(city_name="-").first()

                        jsondata = {"country":country.id, "phone_number":buyer_number, "company_id":last_buyer_company_obj.id, "user_group_type":"administrator", "invited_from":companyName, "state":state.id, "city":city.id}
                        jsondata_res = common_user_registration(jsondata, None, "send_invitee_sms")

                        deleteInviteQuery = Invitee.objects.filter(country=country, invitee_number=buyer_number)
                        try:
                            it = deleteInviteQuery.delete()
                            print "invitee delete ==============", it
                        except Exception as e:
                            logger.info("Exception buyerCSVImportJobs registration error buyer_number = %s , and error = %s"% (str(buyer_number), str(e)))
                            if "request" in str(e):
                                it = deleteInviteQuery.delete()
                                print "invitee delete ==============", it
                            pass
                        '''otpno = random.randrange(100000, 999999, 1)
                        username = str(country.phone_code)+str(buyer_number)
                        username = username.replace("+", "")

                        data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":buyer_number, "country":country.id, "email":str(buyer_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":buyer_name, "invited_from":companyName, "company":last_buyer_company_obj.id, "usertype":"administrator"}
                        register = RegisterSerializer(data=data) #, context={'request': request}
                        if register.is_valid():
                            logger.info("buyerCSVImportJobs save register is_valid = %s"% (str(data)))
                            deleteInviteQuery = Invitee.objects.filter(country=country, invitee_number=buyer_number)
                            try:
                                registerObj = register.save(register)
                                logger.info("registerObj = %s"% (str(registerObj)))
                                it = deleteInviteQuery.delete()
                                print "invitee delete ==============", it
                            except Exception as e:
                                logger.info("Exception buyerCSVImportJobs registration error buyer_number = %s , and error = %s"% (str(buyer_number), str(e)))
                                if "request" in str(e):
                                    it = deleteInviteQuery.delete()
                                    print "invitee delete ==============", it
                                pass
                        else:
                            logger.info("buyerCSVImportJobs is_valid() else registration error buyer_number = %s , and error = %s"% (str(buyer_number), str(register.errors)))'''
                    else:
                        last_buyer_company_obj = add_buyer_v1(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, False, state, city, False, True, jobsObj.action_note, gst, pan);
                        logger.info("last_buyer_company_obj = %s"% (str(last_buyer_company_obj)))

                        wihout_is_raise = last_buyer_company_obj[1]
                        error_detail = last_buyer_company_obj[2]
                        has_relationship = last_buyer_company_obj[3]

                        last_buyer_company_obj = last_buyer_company_obj[0]

                        if wihout_is_raise == False and error_detail is not None and has_relationship == False:
                            if error_detail not in errors_unique:
                                errors_unique.append(error_detail)
                            writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, gst, pan, error_detail,])
                            continue

                        #for bulk buyers
                        '''last_buyer_company_obj = add_buyer(loginUser, loginCompany, buyer_name, country, buyer_number, group_type, False, state, city, True);
                        logger.info("last_buyer_company_obj = %s"% (str(last_buyer_company_obj)))

                        wihout_is_raise = last_buyer_company_obj[1]
                        error_detail = last_buyer_company_obj[2]
                        has_relationship = last_buyer_company_obj[3]

                        last_buyer_company_obj = last_buyer_company_obj[0]
                        if wihout_is_raise == True and last_buyer_company_obj.id not in companyIds: #wihout any error and not appended
                            logger.info("adding into bulk_buyers")
                            companyIds.append(last_buyer_company_obj.id)
                            inviteobj = Invite.objects.create(relationship_type="buyer", company=loginCompany ,user=loginUser)
                            inviteeObj = Invitee.objects.create(invitee_company=last_buyer_company_obj.name,invitee_name=buyer_name,country=country,invitee_number=buyer_number,invite=inviteobj, status="registered", invite_type="userinvitation", invitation_type="Buyer")

                            status='buyer_pending'
                            if last_buyer_company_obj.connections_preapproved == True:
                                status='approved'

                            payment_duration = 0
                            discount = cash_discount = credit_limit = Decimal('0.00')
                            cbg_buyer_type = companyBuyerGroupType(group_type.name)
                            cbgObj = CompanyBuyerGroup.objects.filter(company=loginCompany, buyer_type=cbg_buyer_type).first()
                            if cbgObj:
                                print "cbgObj------", cbgObj
                                discount = cbgObj.discount
                                cash_discount = cbgObj.cash_discount
                                credit_limit = cbgObj.credit_limit
                                payment_duration = cbgObj.payment_duration

                            bulk_buyers.append(Buyer(selling_company = loginCompany, buying_company = last_buyer_company_obj, status=status, group_type=group_type, invitee=inviteeObj, user=loginUser, buying_company_name=buyer_name, buying_person_name=buyer_name, discount=discount, cash_discount=cash_discount, credit_limit=credit_limit, payment_duration=payment_duration))
                        elif wihout_is_raise == False and error_detail is not None and has_relationship == False:
                            if error_detail not in errors_unique:
                                errors_unique.append(error_detail)
                            writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(fields['group_type']), state, city, error_detail,])
                            continue'''

                    last_buyer_name = buyer_name

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()
                except Exception as e:
                    logger.info("buyerCSVImportJobs Inloop Exception - Check csv file and found something wrong around row no =  %s , and error = %s"% (str(column), str(e)))
                    err = {"buyer_csv":"Check csv file and found something wrong around row no = "+str(column)}
                    writer.writerow([str(country_code), str(buyer_number), str(buyer_name), str(group_type_text), state, city, gst, pan, "Found something wrong in this row",])

                    jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                    import traceback
                    jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                    continue

        except Exception as e:
            logger.info("buyerCSVImportJobs Exception - Check csv file and found something wrong around row no = "+str(column))
            logger.info(str(e))
            jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
            import traceback
            jobsObj.exception_details = "Exception = 2, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
            #raise serializers.ValidationError({"buyer_csv":"Check csv file and found something wrong around row no = "+str(column)})

    #for bulk buyers
    '''logger.info("companyIds = %s"% (str(companyIds)))

    logger.info("bulk_buyers = %s"% (str(bulk_buyers)))

    bulk_buyers_status = Buyer.objects.bulk_create(bulk_buyers)
    logger.info("after create bulk_buyers status = %s"% (bulk_buyers_status))

    names = ["Send All","All Distributor","All Wholesaler","All Semi-Wholesaler","All Retailer","All Online-Retailer","All Resellers","All Broker"]
    #names = ["All Broker"]
    ofUserId = loginCompany.chat_admin_user.username #CompanyUser.objects.filter(company=loginCompany).values_list('user__username', flat=True).first()
    logger.info("ofUserId = %s"% (str(ofUserId)))
    groupObjs = BuyerSegmentation.objects.filter(company=loginCompany, buyer_grouping_type="Location Wise", segmentation_name__in=names).exclude(applozic_id__isnull=True)# group_type=self.group_type,
    logger.info("groupObjs = %s"% (str(groupObjs)))
    for groupObj in groupObjs:
        buying_company = Buyer.objects.filter(selling_company=loginCompany, buying_company__in=companyIds, status="approved", group_type__in=groupObj.group_type.all()).values_list('buying_company', flat=True)
        userIds = CompanyUser.objects.filter(company__in=buying_company).values_list('user__username', flat=True).distinct()
        userIds = list(userIds)
        #logger.info(str(userIds))
        logger.info("before group create applozic userIds = %s"% (str(userIds)))
        if len(userIds) > 0:
            r = chat_add_members_in_groups({'clientGroupIds':[str(groupObj.applozic_id)], 'userIds':userIds, 'ofUserId':str(ofUserId)})
    '''

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    #for bulk buyers
    '''notify_buyers = Buyer.objects.filter(selling_company = loginCompany, buying_company__in = companyIds)
    for buyer in notify_buyers:
        logger.info("buyerCSVImportJobs requestNotification")
        requestNotification(buyer.selling_company, None, "buyer", buyer, buyer.buying_company, buyer.status)'''

    #notification to supplier for total sent buyer status
    # image = settings.MEDIA_URL+"logo-single.png"
    title = "Buyer Invite Status"
    jsonarr = {"notId": jobsObj.id, "title":title, "completed_rows":jobsObj.completed_rows, "total_rows":jobsObj.total_rows, "errors":""}

    # message = str(jobsObj.completed_rows)+" invited successfully out of "+str(jobsObj.total_rows)+" requests. "
    print errors_unique
    if len(errors_unique) > 0:
        errors_unique = ', '.join(errors_unique)
        # message += "Unsuccessfull invite reasons could be : "+errors_unique
        jsonarr["errors"] = "Unsuccessfull invite reasons could be : "+errors_unique

    # print "title>>>>>>>>>>>>>>>>>>>>", title
    # print "message>>>>>>>>>>>>>>>>>>>>", message
    # if settings.TASK_QUEUE_METHOD == 'celery':
    #     notificationSend.apply_async(([jobsObj.user.id], message, {"notId": jobsObj.id, "title":title, "push_type":"promotional"}), expires=datetime.now() + timedelta(days=2))
    # elif settings.TASK_QUEUE_METHOD == 'djangoQ':
    #     task_id = async(
    #         'api.tasks.notificationSend',
    #         [jobsObj.user.id], message, {"notId": jobsObj.id, "title":title, "push_type":"promotional"}
    #     )

    user1 = User.objects.filter(id=jobsObj.user.id)
    sendAllTypesMessage("background_task_status", user1, jsonarr)

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections"
            jobsObj.save()
            #return csvresponse
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            #return Response({"success": "Successfully uploaded buyer csv"})
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True

@task()
def supplierCSVImportJobs(job_id):
    logger.info("supplierCSVImportJobs task job_id = %s"% (job_id))
    from api.models import *
    from rest_framework.response import Response
    from django.http import HttpResponse
    from api.common_functions import add_supplier_v1, common_user_registration
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    #from api.v0.serializers import RegisterSerializer
    from api.v1.views import randomString
    import random
    from django.utils import timezone

    logger.info("supplierCSVImportJobs task 1.1")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()
    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name


    logger.info("supplierCSVImportJobs task 1.2")
    '''
    f = jobsObj.upload_file
    first_line = f.readline()[:-1].split(',')
    columns = {}
    i = 0

    logger.info("supplierCSVImportJobs task 1.3")

    for model in first_line:
        columns[model] = i
        i = i+1
    flag = True

    logger.info("supplierCSVImportJobs task 1.4")
    '''
    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    err = ""

    errorfilename = 'jobs_error_file/suppliers_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    errorfile = open(errorfilepath, "wb+")
    writer = csv.writer(errorfile)

    '''csvresponse = HttpResponse(content_type='text/csv')
    csvresponse['Content-Disposition'] = 'attachment; filename="errorbuyers.csv"'
    writer = csv.writer(csvresponse)'''
    writer.writerow(['country_code', 'supplier_number', 'supplier_name', 'group_type', 'state', 'city', 'error'])

    column = 1
    rows = 0
    last_supplier_name = None
    last_supplier_company_obj = None

    country_code = supplier_name = supplier_number = state = city = group_type_text = ""
    fields = {}

    try:
        #for line in f:
        for fields in reader:
            try:
                '''if (flag==True):
                    flag = False
                    continue
                column += 1
                line = line[:-1].split(',')
                fields = {}
                logger.info("line=")
                logger.info(str(line))
                try:
                    for k,v in columns.iteritems():
                        k = re.sub('[^a-zA-Z0-9-_ ]', '',k)
                        fields[k] = re.sub('[^a-zA-Z0-9-_ ]', '',line[v])
                except Exception as e:
                    logger.info("supplierCSVImportJobs Exception - for k,v in columns.iteritems(): row no = "+str(column))
                    logger.info(str(e))
                    continue

                logger.info("fields=")
                logger.info(str(fields))
                '''
                column += 1
                logger.info("json fields = %s"% (str(fields)))

                supplier_name = fields['supplier_name']
                supplier_number = fields['supplier_number']
                state = fields.get('state', None)
                city = fields.get('city', None)

                group_type_text = fields['group_type']
                country_code = fields['country_code']

                if int(supplier_number[0]) in [0,1,2,3,4,5]:
                    logger.info("Mobile number is not valid")
                    err = {"supplier_csv":"Mobile number is not valid : "+str(supplier_number)}
                    writer.writerow([str(country_code), str(supplier_number), str(supplier_name), str(fields['group_type']), state, city, "Mobile number is not valid",])
                    continue

                if not GroupType.objects.filter(name=fields['group_type']).exists():
                    logger.info("Enter a valid group type")
                    err = {"supplier_csv":"Enter a valid group type : "+fields['group_type']}
                    writer.writerow([str(country_code), str(supplier_number), str(supplier_name), str(fields['group_type']), state, city, "Enter a valid group type",])
                    continue

                if not Country.objects.filter(phone_code="+"+country_code).exists():
                    logger.info("Enter a valid country code")
                    err = {"supplier_csv":"Enter a valid country code : "+fields['country_code']}
                    writer.writerow([str(country_code), str(supplier_number), str(supplier_name), str(fields['group_type']), state, city, "Enter a valid country code",])
                    continue

                if not supplier_number.isdigit():
                    err = {"supplier_csv":"Enter a valid supplier number : "+supplier_number}
                    writer.writerow([str(country_code), str(supplier_number), str(supplier_name), str(fields['group_type']), state, city, "Enter a valid supplier number",])
                    continue

                country = Country.objects.get(phone_code="+"+country_code)
                group_type = GroupType.objects.filter(name=fields['group_type']).first()

                #if last_supplier_name is not None and last_supplier_name != "" and last_supplier_name == supplier_name:
                if last_supplier_name is not None and last_supplier_name != "" and last_supplier_name == supplier_name and last_supplier_company_obj is not None:
                    logger.info("supplierCSVImportJobs last_supplier_name is matched with supplier_name")
                    logger.info(str(last_supplier_company_obj))

                    compnumber = getCompanyNumberFromNumber(country, supplier_number)
                    country = compnumber[0]
                    supplier_number = compnumber[1]
                    if Company.objects.filter(country=country, phone_number=supplier_number).exists() or UserProfile.objects.filter(country=country, phone_number=supplier_number).exists():
                        continue

                    if state:
                        state = State.objects.filter(state_name=state).first()
                    if state is None or state == "":
                        state = State.objects.filter(state_name="-").first()

                    if city:
                        city = City.objects.filter(city_name=city, state=state).first()
                    if city is None or city == "":
                        city = City.objects.filter(city_name="-").first()

                    jsondata = {"country":country.id, "phone_number":supplier_number, "company_id":last_supplier_company_obj.id, "user_group_type":"administrator", "invited_from":companyName, "state":state.id, "city":city.id}
                    jsondata_res = common_user_registration(jsondata, None, "send_invitee_sms")

                    deleteInviteQuery = Invitee.objects.filter(country=country, invitee_number=supplier_number)
                    try:
                        it = deleteInviteQuery.delete()
                        print "invitee delete ==============", it
                    except Exception as e:
                        logger.info("Exception supplierCSVImportJobs registration error supplier_number = %s , and error = %s"% (str(supplier_number), str(e)))
                        if "request" in str(e):
                            it = deleteInviteQuery.delete()
                            print "invitee delete ==============", it
                        pass
                    '''otpno = random.randrange(100000, 999999, 1)
                    username = str(country.phone_code)+str(supplier_number)
                    username = username.replace("+", "")

                    data = {"username":username, "password1": otpno, "password2": otpno, "phone_number":supplier_number, "country":country.id, "email":str(supplier_number)+"@wishbooks.io", "number_verified":"no", "is_profile_set":False, "company_name":supplier_name, "invited_from":companyName, "company":last_supplier_company_obj.id, "usertype":"administrator"}
                    register = RegisterSerializer(data=data)#, context={'request': request}
                    if register.is_valid():
                        logger.info("supplierCSVImportJobs save register is_valid")
                        logger.info(str(data))
                        deleteInviteQuery = Invitee.objects.filter(country=country, invitee_number=supplier_number)
                        try:
                            registerObj = register.save(register)
                            print registerObj
                            it = deleteInviteQuery.delete()
                            print "invitee delete ==============", it
                        except Exception as e:
                            logger.info("Exception supplierCSVImportJobs registration error")
                            logger.info(str(supplier_number))
                            logger.info(str(e))
                            if "request" in str(e):
                                it = deleteInviteQuery.delete()
                                print "invitee delete ==============", it
                            pass
                    else:
                        logger.info("supplierCSVImportJobs is_valid() else registration error")
                        #print register.errors
                        logger.info(str(supplier_number))
                        logger.info(str(register.errors))'''
                else:
                    #last_supplier_company_obj = add_supplier(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, False, state, city);
                    last_supplier_company_obj = add_supplier_v1(loginUser, loginCompany, supplier_name, country, supplier_number, group_type, False, state, city);
                last_supplier_name = supplier_name

                rows += 1
                jobsObj.completed_rows=rows
                jobsObj.save()

            except Exception as e:
                logger.info("supplierCSVImportJobs Inloop Exception - Check csv file and found something wrong around row no = "+str(column))
                logger.info(str(e))
                err = {"supplier_csv":"Check csv file and found something wrong around row no = "+str(column)}
                writer.writerow([str(country_code), str(supplier_number), str(supplier_name), str(group_type_text), state, city, "Found something wrong in this row",])

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                continue

    except Exception as e:
        logger.info("supplierCSVImportJobs Exception - Check csv file and found something wrong around row no = "+str(column))
        logger.info(str(e))
        jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
        import traceback
        jobsObj.exception_details = "Exception = 2, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())

    '''try:
        f.close()
    except Exception as e:
        logger.info(str(e))
        pass'''

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections"
            jobsObj.save()
            #return csvresponse
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            #return Response({"success": "Successfully uploaded supplier csv"})
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True

@task()
def dfsShare(pushObj, selling_company, buyers, city, category, group_type, catalogs, catalogSharedProducts, fullCatalogOrders, getObj, is_downstream=False, sendsms=True):
    logger.info("In dfsShare start at "+str(datetime.now()))

    from api.models import *
    from api.v1.serializers import *
    from decimal import Decimal

    logger.info("after import")

    if getObj:
        pushObj = Push.objects.get(pk=pushObj)
        catalogs = Catalog.objects.filter(id__in=catalogs).select_related('brand')
        selling_company = Company.objects.get(pk=selling_company)
        buyers = Buyer.objects.filter(id__in=buyers).select_related('selling_company', 'buying_company')

    logger.info("dfsShare push id = %s"% (str(pushObj.id)))

    logger.info("catalogSharedProducts array = %s" % (catalogSharedProducts))

    index=0
    for catalog in catalogs:
        logger.info("new catalog")
        for product in catalogSharedProducts[index]:
            logger.info("index = %s, product = %s, Push = %s"% (str(index), str(product[0]), str(pushObj.id)))

            productObj=Product.objects.get(pk=product[0])
            price = Decimal(product[2])
            try:
                pspObj, created = PushSellerPrice.objects.get_or_create(push=pushObj, selling_company=selling_company, product=productObj, price = price)
            except Exception as e:
                logger.info("product Exception")
                logger.info(str(e))
                pass
            #pspObj.price = price
            #pspObj.save()
            #PushSellerPrice.objects.create(push=pushObj, selling_company=selling_company, product=productObj, price=price)
            index += 1

    '''if pushObj.buyer_segmentation is not None:
        buyers = Buyer.objects.filter(Q(selling_company = selling_company, status='approved', buying_company__category__in=category, group_type__in=group_type) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company')
    else:
        buyers = Buyer.objects.filter(selling_company = selling_company, status='approved', buying_company=pushObj.single_company_push)'''

    logger.info("before start buyers loop")
    #logger.info(buyers)

    for buyer in buyers:
        logger.info("in loop start buyer")
        completedBuyers = Push_User.objects.filter(push=pushObj).values_list('buying_company', flat=True)
        completedBuyers = list(completedBuyers)
        completedBuyers.extend([selling_company.id])
        if pushObj.company.id == buyer.buying_company.id:
            logger.info("sharing company and buying company are same - continue")
            continue
        #logger.info("completedBuyers = %s" % (completedBuyers))
        logger.info("completedBuyers length = %s" % (len(completedBuyers)))

        if buyer.buying_company.id not in completedBuyers:
            logger.info("sharing to buyer company name ===>> %s, id = %s" % (buyer.buying_company.name, buyer.buying_company.id))

            #logger.info(companyUser.user.username)
            #print companyUser.id
            #logger.info(companyUser)

            #logger.info(catalogs)
            #logger.info(selections)
            index=0

            for catalog in catalogs:
                #print catalog
                totalPrice = 0
                sellingPrice = 0
                #rate = catalogSharedRate[index]
                #fixRate = rate[0]
                #percentageRate = rate[1]
                for product in catalogSharedProducts[index]:
                    #print product

                    productObj=Product.objects.get(pk=product[0])

                    #price = Decimal(product[2]) + (Decimal(product[2])*Decimal(percentageRate)/100) + Decimal(fixRate) ######### , supplier, fixRate, percentageRate
                    price = Decimal(product[2])
                    #logger.info(">>>>product>>>>")
                    #logger.info(product)
                    #logger.info(">>>>price>>>>")
                    #logger.info(price)
                    totalPrice = totalPrice+price
                    sellingPrice=sellingPrice+product[2]

                    cpfObj = CompanyProductFlat.objects.filter(product=productObj, catalog=catalog, buying_company=buyer.buying_company).last()
                    if cpfObj:

                        if cpfObj.final_price >= price or cpfObj.selling_company == selling_company:
                            sellPrice = (price+buyer.fix_amount) + ((price*buyer.percentage_amount)/100)
                            cpfObj.final_price = price
                            cpfObj.selling_price = sellPrice
                            cpfObj.selling_company = selling_company
                            cpfObj.push_reference = pushObj
                            cpfObj.save()
                    else:
                        sellPrice = (price+buyer.fix_amount) + ((price*buyer.percentage_amount)/100)
                        CompanyProductFlat.objects.create(product=productObj, catalog=catalog, buying_company=buyer.buying_company, final_price=price, selling_price=sellPrice, selling_company=selling_company, push_reference=pushObj)


                #logger.info("#########>>>>totalPrice>>>>")
                #logger.info(totalPrice)
                pushuser = Push_User.objects.create(push=pushObj, catalog=catalog, total_price=totalPrice, selling_company=selling_company, buying_company=buyer.buying_company, selling_price=sellingPrice, full_catalog_orders_only=fullCatalogOrders)

                title = catalog.title
                pushImage = catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
                pushName = catalog.title
                companyImage = catalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url

                #sending sms and mobile notifications..
                dfsShareNotification(selling_company, buyer.buying_company, pushObj, catalog, title, "catalog", pushImage, pushName, companyImage, sendsms)

                index+=1
            index=0



            if is_downstream == True and pushObj.push_downstream=="yes" and buyer.buying_company.push_downstream=="yes" and pushObj.buyer_segmentation is not None and pushObj.buyer_segmentation.buyer_grouping_type == "Location Wise":
                logger.info("<<<<<<<<<push_downstream==yes from")
                if  buyer.buying_company.id not in completedBuyers:
                    disableProducts = True
                    if catalogs:
                        disableProducts = CatalogSelectionStatus.objects.filter(company=buyer.buying_company, catalog=catalogs[0], status="Disable").exists()  #values_list('product', flat=True)
                    elif selections:
                        #disableProducts = Push_User_Product.all_objects.filter(selling_company=buyer.buying_company, selection=selections[0], deleted=True).exists()  #values_list('product', flat=True)
                        disableProducts = CatalogSelectionStatus.objects.filter(company=buyer.buying_company, selection=selections[0], status="Disable").exists()

                    if disableProducts:
                        continue

                    '''subBuyers = Buyer.objects.filter(Q(selling_company = buyer.buying_company, status='approved', buying_company__category__in=category) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company') #.values_list('buying_company', flat=True).distinct()  #, group_type__in=group_type
                    '''

                    subBuyers = Buyer.objects.filter(Q(selling_company = buyer.buying_company, status='approved', buying_company__category__in=category, group_type__in=pushObj.buyer_segmentation.group_type.all()) & (Q(buying_company__city__in=city) | Q(buying_company__city__city_name="-"))).distinct().select_related('selling_company', 'buying_company')


                    if subBuyers:# and buyer.buying_company.id not in completedBuyers:
                        logger.info(">>>IF HAS SUB BUYERS total = %s" % (str(subBuyers.count())))

                        newCatalogRate = []
                        buyerRateobj = Buyer.objects.filter(selling_company=buyer.selling_company, buying_company=buyer.buying_company, status="approved").last()
                        famt = buyerRateobj.fix_amount
                        pamt = buyerRateobj.percentage_amount

                        catalogSharedProductsNew = []
                        index1=0
                        for catalog in catalogs:
                            productDObj = []
                            for product in catalogSharedProducts[index1]:
                                price = Decimal(product[2]) + (Decimal(product[2])*Decimal(pamt)/100) + Decimal(famt)
                                productDObj.append([product[0], product[1], price])
                                index1+=1
                            catalogSharedProductsNew.append(productDObj)

                        logger.info("dfsShare Recursion call")

                        '''logger.info("applozic pushserializer msg")
                        ofUserId = buyer.buying_company.chat_admin_user
                        ofUserId = str(ofUserId)
                        nbs = BuyerSegmentation.objects.filter(segmentation_name=pushObj.buyer_segmentation.segmentation_name, company=buyer.buying_company).first()
                        if nbs:
                            #logger.info("nbs")
                            for catalog in catalogs:
                                brandName = catalog.brand.name
                                title = 'catalog ' + catalog.title
                                #message = '%s has shared you a new %s %s' % (brandName, pushType, title)
                                message = '%s has shared you a new %s' % (brandName, title)
                                r = chat_send_message({"ofUserId":ofUserId, "groupId":str(nbs.applozic_id), "message":message})
                                #logger.info("nbs catalog")
                        logger.info("applozic pushserializer msg end")'''


                        catalogs1 = []
                        if catalogs:
                            catalogs1 = catalogs.values_list('id', flat=True)
                        catalogs1 = list(catalogs1)
                        subBuyers = subBuyers.values_list('id', flat=True)
                        subBuyers = list(subBuyers)

                        if settings.TASK_QUEUE_METHOD == 'celery':
                            dfsShare.apply_async((pushObj.id, buyer.buying_company.id, subBuyers, city, category, group_type, catalogs1, catalogSharedProductsNew, fullCatalogOrders, True), expires=datetime.now() + timedelta(days=2))
                        elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                            task_id = async(
                                'api.tasks.dfsShare',
                                pushObj.id, buyer.buying_company.id, subBuyers, city, category, group_type, catalogs1, catalogSharedProductsNew, fullCatalogOrders, True
                            )
        else:
            logger.info("********************/////////allready shared with this buyer company name ===>> %s, id = %s" % (buyer.buying_company.name, buyer.buying_company.id))

    logger.info("In dfsShare end at "+str(datetime.now()))
    return


@task()
def trustedSortOrder():
    from datetime import date, datetime, timedelta
    from api.models import *
    from django.db.models.functions import Concat
    import random

    logger.info("in trustedSortOrder")

    todayDate = date.today()
    monthStartDate = todayDate - timedelta(days=30)
    logger.info("monthStartDate = %s"% (str(monthStartDate)))

    '''print monthStartDate
    monthStartDate = datetime.combine(monthStartDate, datetime.max.time())
    print "monthStartDate =", monthStartDate'''

    Catalog.objects.filter(company__trusted_seller=True, view_permission='public').update(trusted_sort_order=0)

    recent_catalogs = Catalog.objects.filter(company__trusted_seller=True, created_at__gte=monthStartDate, view_permission='public').order_by('-id').distinct().values_list('id', flat=True)
    #recent_catalogs = Catalog.objects.filter().order_by('-id').distinct().values_list('id', flat=True)
    recent_catalogs = list(recent_catalogs)
    logger.info("recent_catalogs = %s"% (str(recent_catalogs)))

    display_catlogs = []
    current_iteration_brands = []
    pending_catalogs = []

    while (len(recent_catalogs) > 0):
        head_catalog = recent_catalogs.pop(0)
        print "head_catalog", head_catalog
        print recent_catalogs
        #for head_catalog in recent_catalogs:
        head_catalog = Catalog.objects.get(pk=head_catalog)
        if head_catalog.brand.id in current_iteration_brands:
            pending_catalogs.append(head_catalog.id)
        else:
            display_catlogs.append(head_catalog.id)
            current_iteration_brands.append(head_catalog.brand.id)

        if len(recent_catalogs) == 0:
            if len(pending_catalogs) == 0:
                break;
            else:
                recent_catalogs = pending_catalogs
                current_iteration_brands = []
                pending_catalogs = []

    logger.info("display_catlogs = %s"% (str(display_catlogs)))
    logger.info("pending_catalogs = %s"% (str(pending_catalogs)))
    logger.info("current_iteration_brands = %s"% (str(current_iteration_brands)))

    Catalog.objects.filter(id__in=pending_catalogs).update(trusted_sort_order=0)

    orderlen = len(display_catlogs)
    for catalogid in display_catlogs:
        logger.info("catalogid = %s , orderlen = %s"% (str(catalogid), str(orderlen)))
        Catalog.objects.filter(id=catalogid).update(trusted_sort_order=orderlen)
        orderlen -= 1

def cancelOrder(salesorder):
    logger.info("in cancelOrder() ========================")
    if salesorder:
        #sObj = SalesOrder.objects.get(pk=salesorder.id)
        if "Cancelled_" not in salesorder.order_number:
            salesorder.order_number = "Cancelled_"+salesorder.order_number+"_"+str(salesorder.id)
        salesorder.processing_status = "Cancelled"
        salesorder.save()
        logger.info(salesorder.processing_status)
        logger.info(salesorder.id)
        #for lsd in last_soObj_data:
        #	writer.writerow(lsd)


#not using below function
@task()
def salesOrderCSVImportJobs(job_id):
    logger.info("salesOrderCSVImportJobs task job_id = %s"% (job_id))
    from api.models import *
    from api.common_functions import getCompanyNumberFromNumber
    from api.v1.serializers import SalesOrderSerializer
    from api.v1.views import getBuyerSupplierProductPrice

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone
    from dateutil.parser import parse
    from datetime import date, datetime, timedelta

    logger.info("salesOrderCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    err = ""

    foldername = 'jobs_error_file/wishbook_salesorder'+str(job_id)+'_'+str(randomString())
    folderpath = os.path.join(settings.MEDIA_ROOT, foldername)
    os.makedirs(folderpath)

    errorfilename = foldername+'/salesorder_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['order_number', 'buyer_name', 'buyer_number', 'catalog', 'sku', 'qty', 'rate', 'packing_type', 'item_remark', 'order_remark', 'broker_number', 'date', 'gst', 'pan', 'state', 'city', 'error_or_success']

    buyer_ids = []
    products = []
    orders = []

    sellingCompanyObj = Buyer.objects.filter(buying_company=loginCompany, status="approved").values_list('selling_company', flat=True).distinct()
    catalogsIds = Push_User.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
    catalogsIds = list(catalogsIds)
    catalogObjs = Catalog.objects.filter(Q(company=loginCompany) | Q(id__in=catalogsIds)) # | Q(view_permission="public")

    # ~ disableCatalogIds = getDisableCatalogIds(loginCompany)
    # ~ catalogObjs = catalogObjs.exclude(id__in=disableCatalogIds)

    #last_companyObj = None
    last_order_number = None
    last_create_err = None
    soObj = None
    last_soObj_data = []

    salesorder = None

    column = 1
    rows = 0
    fields = {}



    error_order_numbers = []
    error_csv_data = []

    order_number_error = "Order Number is required"
    sku_notmatch_error = "SKU not matched"
    catalog_notmatch_error = "Catalog not matched"
    buying_company_notmatch_error = "Buying Company not matched"

    country = Country.objects.get(pk=1)
    aiObj = AppInstance.objects.filter(company=loginCompany).last()

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                #with transaction.atomic():
                for fields in reader:
                    try:
                        column += 1
                        logger.info("json fields = %s"% (str(fields)))

                        order_number = fields['order_number']
                        buyer_name = fields['buyer_name']
                        buyer_number = fields['buyer_number']
                        catalog = fields['catalog']
                        sku = fields['sku']
                        if sku:
                            if sku == "0" or sku==0:
                                sku = ""

                        qty = fields['qty']
                        rate = fields['rate']

                        '''try:
                            logger.info("qty original = %s" % (fields['qty']))
                            qty = int(fields['qty'].split(".")[0])
                            logger.info("qty final = %s" % (qty))

                            logger.info("rate original = %s" % (fields['rate']))
                            rate = Decimal(fields['rate'])
                            logger.info("rate final = %s" % (rate))
                        except Exception as e:
                            logger.info("Qty and Rate Exception = %s" % (e))

                            err = "Please check Qty and Rate and both are required"
                            fields["error_or_success"] = err
                            error_csv_data.append(fields)
                            error_order_numbers.append(order_number)
                            continue;'''

                        packing_type = fields['packing_type']
                        item_remark = fields['item_remark']
                        order_remark = fields['order_remark']

                        date = fields['date']

                        broker_number = fields.get('broker_number', "")

                        gst = fields.get('gst', None)
                        pan = fields.get('pan', None)

                        state = fields.get('state', None)
                        city = fields.get('city', None)


                        # ~ if order_number == "":
                        if order_number == "" and last_order_number is None:
                            err = order_number_error
                            fields["error_or_success"] = err
                            error_csv_data.append(fields)
                            #error_order_numbers.append(order_number)   #order_number is blank so
                            continue;
                        elif order_number == "":
                            order_number = last_order_number
                            fields["order_number"] = order_number   #to save order_number wise in csv so.


                        if gst:
                            if len(str(gst)) != 15:
                                err = "Enter a valid gst"
                                fields["error_or_success"] = err
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                        if pan:
                            if len(str(pan)) != 10:
                                err = "Enter a valid pan"
                                fields["error_or_success"] = err
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                        # ~ if buyer_name == "" and buyer_number == "":
                        if buyer_name == "" and buyer_number == "" and order_number != last_order_number:
                            err = "Buyer Name or Buyer Number is required"
                            fields["error_or_success"] = err
                            error_csv_data.append(fields)
                            error_order_numbers.append(order_number)
                            continue;

                        if buyer_name == "" and buyer_number == "" and last_order_number is None:
                            err = "Buyer Name or Buyer Number is required"
                            #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                            fields["error_or_success"] = err
                            #writer.writerow(fields)
                            error_csv_data.append(fields)
                            error_order_numbers.append(order_number)
                            continue;

                        if qty == "" or rate == "":
                            err = "Qty and Rate are required"
                            #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                            fields["error_or_success"] = err
                            #writer.writerow(fields)
                            error_csv_data.append(fields)
                            error_order_numbers.append(order_number)
                            continue;

                        logger.info("processing order number = "+str(order_number)+" last order number "+ str(last_order_number))

                        if order_number != last_order_number and order_number != "":
                            if salesorder is not None and salesorder.processing_status == "Draft":
                                salesorder.processing_status = "Accepted"
                                salesorder.save()
                                logger.info("Draft to Accepted = %s"% (str(salesorder.processing_status)))
                                salesorder = None


                            companyObj = None

                            kycObj = None
                            if gst:
                                kycObj = CompanyKycTaxation.objects.filter(gstin=gst).first()
                            if pan and kycObj is None:
                                kycObj = CompanyKycTaxation.objects.filter(pan=pan).first()
                            if kycObj:
                                companyObj = kycObj.company

                            if buyer_number != "" and companyObj is None:
                                # compnumber = getCompanyNumberFromNumber(country, buyer_number)
                                # country = compnumber[0]
                                # buyer_number = compnumber[1]
                                #
                                # buyerObj = Buyer.objects.filter(selling_company=loginCompany, buying_company__phone_number=buyer_number).last()
                                # if buyerObj:
                                #     companyObj = buyerObj.buying_company

                                companyObj = getCompanyFromNumber(country, buyer_number)
                                # ~ else:
                                    # ~ cpa = CompanyPhoneAlias.objects.filter(alias_number=buyer_number, status="Approved").last()
                                    # ~ if cpa:
                                        # ~ companyObj = cpa.company

                            if buyer_name != "" and companyObj is None:
                                caObj = CompanyAccount.objects.filter(company=loginCompany, mapped_accout_ref=buyer_name).last()
                                if caObj:
                                    companyObj = caObj.buyer_company
                                else:
                                    #buyerObj = Buyer.objects.filter(Q(selling_company=loginCompany) & Q(Q(buying_company__name=buyer_name) | Q(buying_company_name=buyer_name))).last()
                                    buyerobjs = Buyer.objects.filter(selling_company=loginCompany, buying_company_name=buyer_name, status="approved")
                                    buyer_rel_count = buyerobjs.count()
                                    if buyer_rel_count == 1:
                                        buyerObj = buyerobjs.last()
                                        if buyerObj:
                                            companyObj = buyerObj.buying_company
                                    elif buyer_rel_count > 1:
                                        if state and city:
                                            state = State.objects.filter(state_name=state).first()
                                            city = City.objects.filter(city_name=city).first()

                                            statecity_buyerobjs = buyerobjs.filter(buying_company__address__state=state, buying_company__address__city=city)
                                            if statecity_buyerobjs.count() == 1:
                                                buyerObj = buyerobjs.filter(buying_company__address__state=state, buying_company__address__city=city).last()
                                                if buyerObj:
                                                    companyObj = buyerObj.buying_company
                            print "companyObj ====", companyObj
                            if companyObj is None:
                                err = buying_company_notmatch_error
                                #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                fields["error_or_success"] = err
                                #writer.writerow(fields)
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                            #last_companyObj = companyObj

                            #create new order with buyer details
                            pudata = {}
                            pudata['order_number'] = order_number
                            pudata['customer_status'] = 'Pending'
                            pudata['processing_status'] = 'Draft'
                            pudata['seller_company'] = loginCompany.id
                            pudata['company'] = companyObj.id
                            #pudata['transaction_type'] = 'Sale Purchase'
                            pudata['source_type'] = 'Saas'
                            pudata['order_type'] = 'Credit'
                            pudata['items'] = []
                            pudata['userid'] = loginUser.id


                            if broker_number != "":
                                brokerObj = Buyer.objects.filter(selling_company=loginCompany, buying_company__phone_number=broker_number).last()
                                if brokerObj:
                                    pudata['broker_company'] = brokerObj.buying_company.id

                            logger.info("pudata json = %s"% (str(pudata)))
                            try:
                                #salesorderser = SalesOrderSerializer(data=pudata, context={'request': {'data':{}, 'user':loginUser.id}})#, context={'request': request}
                                salesorderser = SalesOrderSerializer(data=pudata)#, context={'request': request}
                                logger.info("ssssssss=========")
                                if salesorderser.is_valid():
                                    logger.info("order save is_valid")
                                    salesorder = salesorderser.save(user=loginUser)

                                    last_order_number = order_number
                                    if date != "":
                                        #salesorder.created_at = parse(date)
                                        try:
                                            formateddate = datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d %H:%M:%S')
                                            salesorder.created_at = formateddate
                                            salesorder.save()
                                        except Exception as e:
                                            cancelOrder(salesorder)
                                            err = "Change date format to dd/MM/YYYY"
                                            fields["error_or_success"] = err
                                            error_csv_data.append(fields)
                                            error_order_numbers.append(order_number)
                                            continue;
                                    #salesorderSalesOrder.objects.get(pk=soObj.id)

                                    #last_soObj_data.append([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), "Order Cancelled"])

                                else:
                                    logger.info("order save error")
                                    err = salesorderser.errors.values()
                                    logger.info(str(err))
                                    #cancelOrder()
                                    #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                    fields["error_or_success"] = err
                                    #writer.writerow(fields)
                                    error_csv_data.append(fields)
                                    error_order_numbers.append(order_number)
                                    continue;
                            except Exception as e:
                                logger.info("eeeeeeeeee==========")
                                logger.info(str(e))
                                continue
                            logger.info("After salesorder create logic")
                            last_order_number = order_number

                        else:
                            companyObj = salesorder.company #last_companyObj

                        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
                        logger.info("companyObj = %s"% (str(companyObj)))


                        if catalog == "" and sku == "":
                            err = "Catalog or SKU is required"
                            cancelOrder(salesorder)
                            #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                            fields["error_or_success"] = err
                            #writer.writerow(fields)
                            error_csv_data.append(fields)
                            error_order_numbers.append(order_number)
                            continue;

                        try:
                            logger.info("qty original = %s" % (qty))
                            qty = int(qty.split(".")[0])
                            logger.info("qty final = %s" % (qty))

                            logger.info("rate original = %s" % (rate))
                            rate = Decimal(rate)
                            logger.info("rate final = %s" % (rate))
                        except Exception as e:
                            logger.info("Qty and Rate Exception = %s" % (e))

                            cancelOrder(salesorder)

                            err = "Please check Qty and Rate and both are required"
                            fields["error_or_success"] = err
                            error_csv_data.append(fields)
                            error_order_numbers.append(order_number)
                            continue;

                        #aiObj = AppInstance.objects.filter(company=loginCompany).last()

                        catalogObj = None
                        if catalog != "":
                            if aiObj:
                                skumapObj=SKUMap.objects.filter(external_catalog__iexact=catalog, app_instance=aiObj).last()
                                if skumapObj:
                                    catalogObj = skumapObj.catalog

                            if catalogObj is None:
                                catalogObj = catalogObjs.filter(title__iexact=catalog).last()
                            logger.info("catalogObj = %s"% (str(catalogObj)))

                            if catalogObj is None:
                                err = catalog_notmatch_error
                                # ~ if Catalog.objects.filter(id__in=disableCatalogIds, title__iexact=catalog).exists():
                                    # ~ err = "Catalog is disabled"
                                cancelOrder(salesorder)
                                #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                fields["error_or_success"] = err
                                #writer.writerow(fields)
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                        oproducts = []

                        if sku == "":
                            psExcludeIds = ProductStatus.objects.filter(company=loginCompany, product__catalog=catalogObj, status="Disable").values_list('product', flat=True)
                            items = catalogObj.products.exclude(id__in=psExcludeIds)

                            if items.count() == 0:
                                err = "Catalog has no products"
                                cancelOrder(salesorder)
                                fields["error_or_success"] = err
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                            design_wise_qty = get_design_wise_qty(items, qty)
                            logger.info("design_wise_qty = %s"% (str(design_wise_qty)))
                            items = design_wise_qty["items"]
                            dispatch_ind_qty = design_wise_qty["dispatch_ind_qty"]

                            idx = 0
                            #approximate_order = False
                            for product in items:
                                designwiseqty = dispatch_ind_qty[idx]
                                idx = idx + 1
                                if designwiseqty > 0:
                                    oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})

                            '''
                            totalproducts = 0
                            psExcludeIds = ProductStatus.objects.filter(company=loginCompany, product__catalog=catalogObj, status="Disable").values_list('product', flat=True)
                            pu = Push_User.objects.filter(selling_company=loginCompany, buying_company=companyObj, catalog=catalogObj).order_by('-push').first()
                            logger.info("pu = %s"% (str(pu)))
                            if pu:
                                totalproducts = PushSellerPrice.objects.filter(selling_company=loginCompany, product__in=catalogObj.products.all(), push=pu.push).exclude(product__in=psExcludeIds).values_list('product', flat=True).count()
                            if catalogObj.view_permission == "public" and totalproducts == 0:
                                totalproducts = catalogObj.products.exclude(id__in=psExcludeIds).count()

                            if totalproducts == 0 and pu is None and catalogObj.view_permission == "push":
                                #err = "Catalog is not shared with this buyer"
                                #print "1 ?????????????", err
                                #cancelOrder()
                                #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), err])
                                #continue;
                                totalproducts = catalogObj.products.exclude(id__in=psExcludeIds).count()

                            #totalproducts = catalogObj.products.count()
                            logger.info("totalproducts = %s"% (str(totalproducts)))
                            if totalproducts == 0:
                                err = "Catalog has no products"
                                cancelOrder(salesorder)
                                #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                fields["error_or_success"] = err
                                #writer.writerow(fields)
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                            designwiseqty = float(qty)/ totalproducts

                            logger.info("designwiseqty = %s"% (str(designwiseqty)))
                            if (qty % totalproducts) > 0:
                                #shouldbeqty = (round(designwiseqty)) * totalproducts
                                #err = "Number of designs not matched (should be "+str(shouldbeqty)+", whereas qty "+str(qty)+" uploaded)"
                                err = "Qty should be the multiple of "+str(totalproducts)+" (no. of designs in this catalog)"
                                cancelOrder(salesorder)
                                fields["error_or_success"] = err
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;

                            if pu is None and catalogObj.view_permission == "push":
                                #err = "Catalog is not shared with this buyer"
                                for product in catalogObj.products.exclude(id__in=psExcludeIds):
                                    oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
                            else:
                                #price matching for shared catalog
                                if totalproducts > 0 and pu is not None:
                                    pspObjs = PushSellerPrice.objects.filter(selling_company=loginCompany, product__in=catalogObj.products.all(), push=pu.push)
                                    is_loop_break = False
                                    for pspObj in pspObjs:
                                        shared_price = getBuyerSupplierProductPrice(companyObj, loginCompany, pspObj.product)
                                        logger.info("shared_price ============= %s"% (str(shared_price)))
                                        # ~ if shared_price is None:
                                            # ~ err = "Buyer doesn't received all products of this catalog"
                                            # ~ cancelOrder(salesorder)
                                            # ~ #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                            # ~ fields["error_or_success"] = err
                                            # ~ #writer.writerow(fields)
                                            # ~ error_csv_data.append(fields)
                                            # ~ error_order_numbers.append(order_number)
                                            # ~ is_loop_break = True
                                            # ~ break

                                        # ~ if Decimal(shared_price) != Decimal(rate):
                                            # ~ err = "Price not matched (should be "+str(shared_price)+" instead of "+str(rate)+" uploaded)"
                                            # ~ cancelOrder(salesorder)
                                            # ~ #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                            # ~ fields["error_or_success"] = err
                                            # ~ #writer.writerow(fields)
                                            # ~ error_csv_data.append(fields)
                                            # ~ error_order_numbers.append(order_number)
                                            # ~ is_loop_break = True
                                            # ~ break

                                        oproducts.append({"product":pspObj.product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
                                    if is_loop_break:
                                        continue
                                #price matching for public catalog
                                else:
                                    is_loop_break = False
                                    for product in catalogObj.products.all():
                                        shared_price = getBuyerSupplierProductPrice(companyObj, loginCompany, product)
                                        logger.info("shared_price ============= %s"% (str(shared_price)))

                                        # ~ if Decimal(shared_price) != Decimal(rate):
                                            # ~ err = "Price not matched (should be "+str(shared_price)+" instead of "+str(rate)+" uploaded)"
                                            # ~ cancelOrder(salesorder)
                                            # ~ #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                            # ~ fields["error_or_success"] = err
                                            # ~ #writer.writerow(fields)
                                            # ~ error_csv_data.append(fields)
                                            # ~ error_order_numbers.append(order_number)
                                            # ~ #continue;
                                            # ~ is_loop_break = True
                                            # ~ break

                                        oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
                                    if is_loop_break:
                                        continue
                            '''
                        #single sku handling
                        else:
                            designwiseqty = qty
                            logger.info("designwiseqty = %s"% (str(designwiseqty)))

                            product = None
                            #aiObj = AppInstance.objects.filter(company=loginCompany).last()
                            if aiObj:
                                skumapObj=SKUMap.objects.filter(external_sku__iexact=sku, app_instance=aiObj).last()
                                if skumapObj:
                                    product = skumapObj.product

                            if product is None:
                                if catalogObj:
                                    product = catalogObj.products.filter(sku__iexact=sku).last()
                                else:
                                    product = Product.objects.filter(sku__iexact=sku, catalog__in=catalogObjs).last()

                            logger.info("product = %s"% (str(product)))
                            if product is None:
                                err = sku_notmatch_error
                                cancelOrder(salesorder)
                                #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                fields["error_or_success"] = err
                                #writer.writerow(fields)
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;
                            # ~ shared_price = getBuyerSupplierProductPrice(companyObj, loginCompany, product)

                            # ~ logger.info("shared_price ============= %s"% (str(shared_price)))
                            '''
                            if Decimal(shared_price) != Decimal(rate):
                                err =  "Price not matched (should be "+str(shared_price)+" instead of "+str(rate)+" uploaded)"
                                cancelOrder(salesorder)
                                #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), err])
                                fields["error_or_success"] = err
                                #writer.writerow(fields)
                                error_csv_data.append(fields)
                                error_order_numbers.append(order_number)
                                continue;
                            '''
                            #products[buyer_index].append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})
                            oproducts.append({"product":product.id,"quantity":designwiseqty,"rate":rate,"packing_type":packing_type,"note":item_remark})

                        logger.info("before saving order items: ============= %s"% (str(oproducts)))
                        #print salesorder
                        print salesorder.id
                        #saving order items
                        for product in oproducts:
                            productobj = Product.objects.get(pk=product["product"])
                            salesitem = SalesOrderItem.objects.get_or_create(product=productobj, quantity=product["quantity"], rate=product["rate"], sales_order = salesorder, pending_quantity=product["quantity"], note=product["note"], packing_type=product["packing_type"])
                            logger.info("successfully saved order items")

                        #writer.writerow([str(order_number), str(buyer_name), str(buyer_number), str(catalog), str(sku), str(qty), str(rate), str(packing_type), str(item_remark), str(order_remark), str(broker_number), "Success"])
                        fields["error_or_success"] = "Success"
                        #writer.writerow(fields)
                        error_csv_data.append(fields)
                        #error_order_numbers.append(order_number)   #sucess order so don't need to create an error

                        rows += 1
                        jobsObj.completed_rows=rows
                        jobsObj.save()

                    except Exception as e:
                        logger.info("salesOrderCSVImportJobs Exception = 1, forloop error = %s"% (str(e)))
                        err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                        jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                        import traceback
                        jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                        jobsObj.save()
                        pass

                if salesorder is not None and salesorder.processing_status == "Draft":
                    salesorder.processing_status = "Accepted"
                    salesorder.save()
                    salesorder = None

            except Exception as e:
                logger.info("salesOrderCSVImportJobs Exception = 2, start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                import traceback
                jobsObj.exception_details = "Exception = 2, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                jobsObj.save()
                pass

            try:
                for errorcsv in error_csv_data:
                    if errorcsv["order_number"] in error_order_numbers or errorcsv["error_or_success"] == order_number_error:
                        #if errorcsv["error_or_success"] == "Success":
                        #    errorcsv["error_or_success"] = "Cancelled due to other rows errors"
                        writer.writerow(errorcsv)

                        if "Order number already exists" in str(errorcsv["error_or_success"]):
                            #continue to not cancel order
                            continue

                        try:
                            salesorder = SalesOrder.objects.filter(order_number=errorcsv["order_number"], seller_company=loginCompany.id).first()
                            cancelOrder(salesorder)
                        except Exception as e:
                            logger.info("salesOrderCSVImportJobs for errorcsv in error_csv_data: Exception error = %s"% (str(e)))
                            pass
            except Exception as e:
                pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()



    logger.info("skucatalogmapfilepath start====")

    skucatalogmapfilename = foldername+'/skucatalogmap_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    skucatalogmapfilepath = os.path.join(settings.MEDIA_ROOT, skucatalogmapfilename)
    fieldnames = ['wishbook_sku', 'external_sku', 'wishbook_catalog', 'external_catalog', 'error']

    with open(skucatalogmapfilepath, "wb") as out_filesc:
        writer = csv.DictWriter(out_filesc, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        try:
            for errorcsv in error_csv_data:
                if errorcsv["error_or_success"] == sku_notmatch_error or errorcsv["error_or_success"] == catalog_notmatch_error:
                    errorjson = {"wishbook_sku":"", "external_sku":"", "wishbook_catalog":"", "external_catalog":"", "error":errorcsv["error_or_success"]}

                    if errorcsv["error_or_success"] == sku_notmatch_error:
                        errorjson["external_sku"] = errorcsv["sku"]

                        catalogObj = None
                        catalog = errorcsv["catalog"]

                        if catalog:
                            if aiObj:
                                skumapObj=SKUMap.objects.filter(external_catalog__iexact=catalog, app_instance=aiObj).last()
                                if skumapObj:
                                    catalogObj = skumapObj.catalog
                                    errorjson["external_catalog"] = catalog

                            if catalogObj is None:
                                catalogObj = catalogObjs.filter(title__iexact=catalog).last()

                            if catalogObj:
                                errorjson["wishbook_catalog"] = catalogObj.title

                    if errorcsv["error_or_success"] == catalog_notmatch_error:
                        errorjson["external_catalog"] = errorcsv["catalog"]

                    writer.writerow(errorjson)
        except Exception as e:
            import traceback
            print "skucatalogmap Exception =", traceback.format_exc()
            pass

    logger.info("skucatalogmapfilepath done====")
    logger.info(skucatalogmapfilepath)



    logger.info("companymapfilepath start====")

    companymapfilename = foldername+'/companymap_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    companymapfilepath = os.path.join(settings.MEDIA_ROOT, companymapfilename)
    fieldnames = ['wishbook_company', 'external_company', 'error']

    with open(companymapfilepath, "wb") as out_filesc:
        writer = csv.DictWriter(out_filesc, delimiter=',', fieldnames=fieldnames)
        writer.writeheader()
        try:
            for errorcsv in error_csv_data:
                if errorcsv["error_or_success"] == buying_company_notmatch_error:
                    errorjson = {"wishbook_company":"", "external_company":"", "error":errorcsv["error_or_success"]}

                    if errorcsv["buyer_name"] != "":
                        errorjson["external_company"] = errorcsv["buyer_name"]
                    elif errorcsv["buyer_number"] != "":
                        errorjson["external_company"] = errorcsv["buyer_number"]

                    writer.writerow(errorjson)
        except Exception as e:
            import traceback
            print "companymap Exception =", traceback.format_exc()
            pass

    logger.info("companymapfilepath done====")
    logger.info(companymapfilepath)



    # if jobsObj.action_note:
    #     try:
    #         invoiceshipment_job_id = int(jobsObj.action_note)
    #         newJobsObjShipmentSO = Jobs.objects.get(pk=invoiceshipment_job_id)
    #
    #         if settings.TASK_QUEUE_METHOD == 'celery':
    #             task_id = shipmentCSVImportJobs.apply_async((newJobsObjShipmentSO.id, False,), expires=datetime.now() + timedelta(days=2))
    #         elif settings.TASK_QUEUE_METHOD == 'djangoQ':
    #             task_id = async(
    #                 'api.tasks.shipmentCSVImportJobs',
    #                 newJobsObjShipmentSO.id, False,
    #                 broker = priority_broker
    #             )
    #
    #         #jobsObj.action_note = None
    #         #jobsObj.save()
    #
    #     except Exception as e:
    #         pass



    if err != "":
        try:
            logger.info("error file save to error_file err = %s" %(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)

            import shutil
            zipres = shutil.make_archive(folderpath, "zip", folderpath)
            print zipres

            if wrong_csv_uploaded is False:
                jobsObj.error_file=foldername+".zip"
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True

def disableCatalogNotification(catalog, sellercompany):
    from api.models import CompanyUser, UnsubscribedNumber, UserProfile
    from django.db.models.functions import Concat
    from api.common_functions import *

    logger.info("in disableCatalogNotification")
    logger.info("catalog id = %s, expire date = %s"% (str(catalog.id), str(catalog.expiry_date)))
    #users = CompanyUser.objects.filter(company=catalog.company, user__groups__name="administrator").values_list('user', flat=True)
    users = CompanyUser.objects.filter(company=sellercompany, user__groups__name="administrator").values_list('user', flat=True)
    users = list(users)
    print users
    image = catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
    companyImage = catalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url
    #message = "Your catalog "+str(catalog.title)+" has been disabled. To enable again, touch 'Start Selling Again' button"
    message = "Aapka catalog "+str(catalog.title)+" disable ho gaya hai. Fir se enable karne ke liye 'Start Selling Again' pe touch kare"

    if settings.TASK_QUEUE_METHOD == 'celery':
        notificationSend.apply_async((users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":image, "company_image":companyImage, "title":"Catalog expire", "name":catalog.title, "table_id": int(catalog.id)}), expires=datetime.now() + timedelta(days=2))
    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        task_id = async(
            'api.tasks.notificationSend',
            users, message, {"push_id": int(catalog.id),"notId":int(catalog.id),"push_type":"catalog","image":image, "company_image":companyImage, "title":"Catalog expire", "name":catalog.title, "table_id": int(catalog.id)}
        )

    unsubscribed_number = UnsubscribedNumber.objects.all().annotate(phone=Concat('country__phone_code','phone_number')).values_list('phone', flat=True).distinct()

    smsUser = UserProfile.objects.filter(user__in=users, user__groups__name="administrator")
    for userPObj in smsUser:
        if "+91" not in userPObj.country.phone_code:
            continue

        phone_number = [str(userPObj.country.phone_code)+str(userPObj.phone_number)]
        phone_number = list(set(phone_number) - set(unsubscribed_number))

        if len(phone_number) == 0:
            continue

        otp = getLastOTP(userPObj)
        smsurl = 'https://app.wishbooks.io/m?type=catalog&id='+str(catalog.id)
        usersmsurl = smsurl + '&m='+str(userPObj.phone_number)+'&o='+str(otp)
        usersmsurl = urlShortener(usersmsurl)

        template = smsTemplates("disable_catalog")% (catalog.title, usersmsurl)

        logger.info("in_queue disableCatalogNotification smsSendTextNationPromotional")
        if settings.TASK_QUEUE_METHOD == 'celery':
            smsSendTextNationPromotional.apply_async((phone_number, template, True), expires=datetime.now() + timedelta(days=2))
        elif settings.TASK_QUEUE_METHOD == 'djangoQ':
            task_id = async(
                'api.tasks.smsSendTextNationPromotional',
                phone_number, template, True
            )

'''
def disableCatalogSellerNotification(catalogSellerObj):
    from api.models import CompanyUser
    logger.info("in disableCatalogSellerNotification")
    logger.info("catalog id = %s, expire date = %s"% (str(catalogSellerObj.catalog.id), str(catalogSellerObj.expiry_date)))
    users = CompanyUser.objects.filter(company=catalogSellerObj.selling_company, user__groups__name="administrator").values_list('user', flat=True)
    users = list(users)
    print users
    image = catalogSellerObj.catalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
    companyImage = catalogSellerObj.catalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url
    message = "Your catalog "+str(catalogSellerObj.catalog.title)+" has been disabled. To enable again, touch 'Start Selling Again' button"

    if settings.TASK_QUEUE_METHOD == 'celery':
        notificationSend.apply_async((users, message, {"push_id": int(catalogSellerObj.catalog.id),"notId":int(catalogSellerObj.catalog.id),"push_type":"catalog","image":image, "company_image":companyImage, "title":"Catalog expire", "name":catalogSellerObj.catalog.title, "table_id": int(catalogSellerObj.catalog.id)}), expires=datetime.now() + timedelta(days=2))
    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        task_id = async(
            'api.tasks.notificationSend',
            users, message, {"push_id": int(catalogSellerObj.catalog.id),"notId":int(catalogSellerObj.catalog.id),"push_type":"catalog","image":image, "company_image":companyImage, "title":"Catalog expire", "name":catalogSellerObj.catalog.title, "table_id": int(catalogSellerObj.catalog.id)}
        )
'''

@task()
def disableCatalog():
    from datetime import date, datetime, timedelta
    from api.models import *
    from django.db.models.functions import Concat
    import random

    logger.info("in disableCatalog")

    todayDate = date.today()
    todayDate = datetime.combine(todayDate, datetime.max.time())
    logger.info("todayDate = %s"% (str(todayDate)))

    #for testing reason
    #~ tempdate = todayDate - timedelta(days=10)
    #~ print tempdate
    #~ Catalog.objects.all().update(supplier_disabled=False)
    #~ Push_User.objects.all().update(supplier_disabled=False, buyer_disabled=False)
    #~ CatalogSeller.objects.all().update(status="Enable")
    #~ Catalog.objects.filter(expiry_date__isnull=True).update(expiry_date=tempdate)
    #~ Push_User.objects.filter(expiry_date__isnull=True).update(expiry_date=tempdate)
    #~ CatalogSelectionStatus.objects.all().delete()

    #return True


    #will filter till yesterday
    catalogs = Catalog.objects.filter(expiry_date__lte=todayDate, supplier_disabled=False)
    logger.info("total catalogs = %s"% (str(catalogs.count())))

    for catalog in catalogs:
        logger.info("catalog id = %s, expire date = %s"% (str(catalog.id), str(catalog.expiry_date)))

        psObj, created = CatalogSelectionStatus.objects.get_or_create(company=catalog.company, catalog=catalog)
        if psObj.status == "Enable":
            logger.info("company id = %s, Disable in if cond."% (str(catalog.company.id)))
            psObj.status="Disable"
            psObj.save()

        catalog.supplier_disabled = True
        catalog.save()

        Push_User.objects.filter(selling_company=catalog.company, catalog=catalog).update(supplier_disabled=False)
        Push_User.objects.filter(buying_company=catalog.company, catalog=catalog).update(buyer_disabled=False)
        csObjs = CatalogSeller.objects.filter(selling_company=catalog.company, catalog=catalog)#.update(status="Disable")
        for csObj in csObjs:
			csObj.status="Disable"
			csObj.save()

        disableCatalogNotification(catalog, catalog.company)

        #Push_User.objects.filter(catalog=catalog, expiry_date__lte=todayDate).update(supplier_disabled=True, buyer_disabled=True)

        buying_companies = Push_User.objects.filter(catalog=catalog, expiry_date__lte=todayDate, buyer_disabled=False).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
        logger.info("buying_companies = %s"% (str(buying_companies)))
        companies = Company.objects.filter(id__in=buying_companies)
        for company in companies:
            logger.info("push_user company = %s, Disable"% (str(company.id)))
            psObj, created = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=catalog)
            if psObj.status == "Enable":
                logger.info("company id = %s, Disable in if cond."% (str(company.id)))
                psObj.status="Disable"
                psObj.save()

        Push_User.objects.filter(catalog=catalog, expiry_date__lte=todayDate, buyer_disabled=False).exclude(buying_company__isnull=True).update(buyer_disabled=True)

    #return True
    logger.info("=====================================================")
    #catalogs = Push_User.objects.filter(Q(expiry_date__lte=todayDate) & Q(Q(supplier_disabled=False) | Q(buyer_disabled=False))).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
    catalogs = Push_User.objects.filter(expiry_date__lte=todayDate, buyer_disabled=False).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
    catalogs = Catalog.objects.filter(id__in=catalogs)
    logger.info("total shared catalogs = %s"% (str(catalogs.count())))

    for catalog in catalogs:
        logger.info("shared catalog id = %s"% (str(catalog.id)))

        #buying_companies = Push_User.objects.filter(Q(Q(catalog=catalog) & Q(expiry_date__lte=todayDate)) & Q(Q(supplier_disabled=False) | Q(buyer_disabled=False))).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
        buying_companies = Push_User.objects.filter(catalog=catalog, expiry_date__lte=todayDate, buyer_disabled=False).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
        logger.info("buying_companies = %s"% (str(buying_companies)))

        companies = Company.objects.filter(id__in=buying_companies)
        for company in companies:
            logger.info("push_user company = %s, Disable"% (str(company.id)))
            psObj, created = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=catalog)
            if psObj.status == "Enable":
                logger.info("company id = %s, Disable in if cond."% (str(company.id)))
                psObj.status="Disable"
                psObj.save()

        Push_User.objects.filter(catalog=catalog, expiry_date__lte=todayDate, buyer_disabled=False).exclude(buying_company__isnull=True).update(buyer_disabled=True)

    #return True
    logger.info("=====================================================")
    csObjs = CatalogSeller.objects.filter(expiry_date__lte=todayDate, status="Enable")
    logger.info("total CatalogSeller catalogs = %s"% (str(csObjs.count())))

    for csObj in csObjs:
        logger.info("CatalogSeller id = %s"% (str(csObj.id)))

        psObj, created = CatalogSelectionStatus.objects.get_or_create(company=csObj.selling_company, catalog=csObj.catalog)
        if psObj.status == "Enable":
            logger.info("company id = %s, Disable in if cond."% (str(csObj.selling_company.id)))
            psObj.status="Disable"
            psObj.save()
        csObj.status = "Disable"
        csObj.save()

        if csObj.catalog.company == csObj.selling_company:
            csObj.catalog.supplier_disabled = True
            csObj.catalog.save()

        #disableCatalogSellerNotification(csObj)
        disableCatalogNotification(csObj.catalog, csObj.selling_company)

    '''logger.info("=====================================================")
    tomorrowDate = todayDate + timedelta(days=1)
    logger.info("tomorrowDate = %s"% (str(tomorrowDate)))

    notifycatalogs = Catalog.objects.filter(expiry_date__gte=todayDate, supplier_disabled=False, expiry_date__lte=tomorrowDate)
    logger.info("total notifycatalogs = %s"% (str(notifycatalogs.count())))

    for notifycatalog in notifycatalogs:
        logger.info("notifycatalog id = %s, expire date = %s"% (str(notifycatalog.id), str(notifycatalog.expiry_date)))
        users = CompanyUser.objects.filter(company=notifycatalog.company, user__groups__name="administrator").values_list('user', flat=True)
        users = list(users)
        print users
        image = notifycatalog.thumbnail.thumbnail[settings.MEDIUM_IMAGE].url
        companyImage = notifycatalog.brand.image.thumbnail[settings.MEDIUM_IMAGE].url
        message = "Your catalog "+str(notifycatalog.title)+" will expire tomorrow"

        if settings.TASK_QUEUE_METHOD == 'celery':
            notificationSend.apply_async((users, message, {"push_id": int(notifycatalog.id),"notId":int(notifycatalog.id),"push_type":"catalog","image":image, "company_image":companyImage, "title":"Catalog expire", "name":notifycatalog.title, "table_id": int(notifycatalog.id)}), expires=datetime.now() + timedelta(days=2))
        elif settings.TASK_QUEUE_METHOD == 'djangoQ':
            task_id = async(
                'api.tasks.notificationSend',
                users, message, {"push_id": int(notifycatalog.id),"notId":int(notifycatalog.id),"push_type":"catalog","image":image, "company_image":companyImage, "title":"Catalog expire", "name":notifycatalog.title, "table_id": int(notifycatalog.id)}
            )'''

@task()
def ProductEAV():
    from api.models import Product
    from api.common_functions import productEAVset
    from api.cache_functions import *

    logger.info("in Cache testing Start")

    deleteCache("public")
    deleteCache("most_viewed")
    deleteCache("most_ordered")
    deleteCache("trusted_seller")

    try:
        logger.info("in Cache testing 4 public          = %s" % (getCache("public")))

        logger.info("in Cache testing 1 most_viewed     = %s" % (getCache("most_viewed")))
        logger.info("in Cache testing ids 1 most_viewed     = %s" % (getCache("most_viewed").values_list('id', flat=True)))
        logger.info("in Cache testing 2 most_ordered    = %s" % (getCache("most_ordered")))
        logger.info("in Cache testing ids 2 most_ordered    = %s" % (getCache("most_ordered").values_list('id', flat=True)))
        logger.info("in Cache testing ids 3 trusted_seller  = %s" % (getCache("trusted_seller").values_list('id', flat=True)))
        logger.info("in Cache testing ids 4 public          = %s" % (getCache("public").values_list('id', flat=True)))

    except Exception as e:
        import traceback
        logger.info("in Cache testing Exception     e = %s,    traceback.format_exc() = %s" % (e, traceback.format_exc()))



    logger.info("in Cache testing End")

    # logger.info("in ProductEAV Start")
    # productObjs = Product.objects.all().order_by('-id')
    # for product in productObjs:
    #     logger.info("ProductEAV product id = %s"% (str(product.id)))
    #     if product.catalog is not None and product.catalog.category is not None:
    #         try:
    #             productEAVset(product)
    #         except Exception:
    #             pass
    # logger.info("in ProductEAV Done")

@task()
def CatalogEAV():
    from api.models import *
    from api.common_functions import catalogEAVset

    logger.info("in CatalogEAV Start")

    catalogObjs = Catalog.objects.all().order_by('-id')
    #catalogObjs = Catalog.objects.filter(id=526).order_by('id')
    for catalog in catalogObjs:
        logger.info("CatalogEAV catalog id = %s"% (str(catalog.id)))
        try:
            catalogEAVset(catalog)
        except Exception as e:
            logger.info("In CatalogEAV Exception")
            logger.info(str(e))
            pass

    logger.info("in CatalogEAV Done")

@task()
def BrandTotalCatalog():
    from api.models import *
    logger.info("in BrandTotalCatalog Start")

    Brand.objects.filter(total_catalog__gt = 0).update(total_catalog=0)
    brandids = Catalog.objects.filter(view_permission="public", supplier_disabled=False).order_by('brand').values_list('brand', flat=True).distinct()
    for brandid in brandids:
        logger.info("BrandTotalCatalog brand id = %s"% (brandid))
        total_catalog = Catalog.objects.filter(view_permission="public", supplier_disabled=False, brand=brandid).count()
        Brand.objects.filter(id=brandid).update(total_catalog=total_catalog)

    #can use below logic. #not used yet
    '''dtnow = datetime.now()
    brandids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow).values_list('catalog__brand', flat=True).distinct()
    for brandid in brandids:
        logger.info("BrandTotalCatalog brand id = %s"% (brandid))
        cids = CatalogSeller.objects.filter(selling_type="Public", status="Enable", expiry_date__gt=dtnow, catalog__brand=brandid).values_list('catalog', flat=True).distinct()
		total_catalog = Product.objects.filter(catalog__view_permission="public", catalog__in=cids).values_list('catalog', flat=True).distinct().count()
        Brand.objects.filter(id=brandid).update(total_catalog=total_catalog)'''

    logger.info("in BrandTotalCatalog Done")

@task()
def CompanySellsToStateTask():
    from api.models import *
    logger.info("in CompanySellsToStateCron Start")

    CompanySellsToState.objects.all().delete()

    companyids = Catalog.objects.filter(view_permission="public", supplier_disabled=False).order_by('company').values_list('company', flat=True).distinct()
    companyObjs = Company.objects.filter(id__in=companyids).exclude(address__state__state_name="-").order_by('id')
    for companyObj in companyObjs:
        logger.info("CompanySellsToStateCron companyObj = %s"% (companyObj.id))
        CompanySellsToState.objects.get_or_create(company=companyObj, state=companyObj.address.state, intermediate_buyer=None)

        buyerObjs = Buyer.objects.filter(Q(selling_company=companyObj) & Q(Q(buying_company__company_group_flag__manufacturer=True) | Q(buying_company__company_group_flag__wholesaler_distributor=True) | Q(buying_company__company_group_flag__broker=True))).exclude(Q(buying_company__address__state = companyObj.address.state) | Q(buying_company__address__state__state_name="-"))
        #buyerObjs = Buyer.objects.filter(Q(selling_company=companyObj) & Q(Q(buying_company__group_type__name="Wholesaler") | Q(buying_company__group_type__name="Broker") | Q(buying_company__group_type__name=""))).exclude(buying_company__address__state = companyObj.address.state)
        for buyerObj in buyerObjs:
            logger.info("CompanySellsToStateCron buyerObj = %s"% (buyerObj.id))
            CompanySellsToState.objects.get_or_create(company=companyObj, state=buyerObj.buying_company.address.state, intermediate_buyer=buyerObj.buying_company)

    logger.info("in CompanySellsToStateCron Done")

@task()
def GEOCodeLocationTask():
    from api.models import *
    import time

    logger.info("in GEOCodeLocationCron Start")
    limit = 0
    meetings = Meeting.objects.filter(location_address__isnull=True).order_by('-id') #[:1]

    for meeting in meetings:
        #time.sleep(100.0 / 1000.0);#1/10 second
        time.sleep(200.0 / 1000.0);
        logger.info("GEOCodeLocation meeting id = %s"% (str(meeting.id)))

        geocodeObj = geocode(meeting.start_lat, meeting.start_long)
        #print geocodeObj
        if geocodeObj['status'] == "OK":
            city = state = None
            components = geocodeObj['results'][0]['address_components']
            for component in components:
                if component['types'][0] == "administrative_area_level_2":
                    city = component['long_name']
                if component['types'][0] == "administrative_area_level_1":
                    state = component['long_name']
            print city, state
            meeting.location_address = geocodeObj['results'][0]['formatted_address']
            meeting.location_city = city
            meeting.location_state = state
            meeting.save()
        elif geocodeObj['status'] == "OVER_QUERY_LIMIT":
            limit += 1
            print "limit =",limit
            if limit == 10:
                break

    limit = 0
    addresses = Address.objects.filter(location_address__isnull=True, latitude__isnull=False, longitude__isnull=False).order_by('-id')#[:1]

    for address in addresses:
        #time.sleep(100.0 / 1000.0);#1/10 second
        time.sleep(200.0 / 1000.0);
        logger.info("GEOCodeLocation address id = %s"% (str(address.id)))

        geocodeObj = geocode(address.latitude, address.longitude)
        print geocodeObj
        if geocodeObj['status'] == "OK":
            city = state = pincode =None
            components = geocodeObj['results'][0]['address_components']
            for component in components:
                if component['types'][0] == "administrative_area_level_2":
                    city = component['long_name']
                if component['types'][0] == "administrative_area_level_1":
                    state = component['long_name']
                if component['types'][0] == "postal_code":
                    pincode = component['long_name']
            print city, state
            address.location_address = geocodeObj['results'][0]['formatted_address']
            address.location_city = city
            address.location_state = state
            if address.pincode is None and pincode is not None:
                if pincode.isdigit():
                    address.pincode = int(pincode)
            if address.state.state_name=="-" or address.city.city_name=="-":
                stateObj = State.objects.filter(state_name=state).first()
                if stateObj :
                    address.state=stateObj

                cityObj = City.objects.filter(city_name=city).first()
                if cityObj :
                    address.city=cityObj

            address.save()
        elif geocodeObj['status'] == "OVER_QUERY_LIMIT":
            limit += 1
            print "limit =",limit
            if limit == 10:
                break

    logger.info("in GEOCodeLocationCron Done")

@task()
def checkOTPVerifyStatusNSendSMS(phone_number, otp):
    from api.models import RegistrationOTP
    import time

    logger.info("in checkOTPVerifyStatusNSendSMS Start")

    phone_number_temp = phone_number.replace("+", "")
    phone_number_temp = phone_number_temp[-10:]

    registrationOtp = RegistrationOTP.objects.filter(phone_number=phone_number_temp, otp=otp).order_by('-id').first()
    if registrationOtp is not None and registrationOtp.is_verified == "no":
        logger.info("Re-sending OTP in cron")
        url = 'https://2factor.in/API/V1/74b6c0fa-f781-11e7-a328-0200cd936042/SMS/%s/%s/WishbookOTP'% (phone_number, otp)
        #url = 'https://2factor.in/API/V1/xxxxxxxx-xxxxx-xxxxxx-xxxxxxxx-xxxxxxxxxxxxxxxx/SMS/%s/%s/WishbookOTP'% (phone_number, otp)
        sendsmart = requests.get(url)

        logger.info("Re-sending OTP status = %s, json = %s"% (sendsmart, sendsmart.json()))

        sendsmart = sendsmart.json()

        if sendsmart["Status"] == "Success":
            smsTrasaction("2factor", 1)
        else:
            mail_status = send_mail("SMS 2factor", "Error = "+str(sendsmart)+" & mobile no = "+str(phone_number)+" & template = "+url, "tech@wishbook.io", ["tech@wishbook.io"])
            logger.info(str(mail_status))
            #SmsError.objects.create(sms_text=message, mobile_no=str(mobile_nos[i]), provider="sendsmart", error_text=str(sendsmart.text))

    logger.info("in checkOTPVerifyStatusNSendSMS Done")
    return True


@task()
def UserContactRegistrationTask():
    from api.common_functions import common_user_registration, getCompanyNumberFromNumber, smsSend, urlShortener, getLastOTP
    from api.models import RegistrationOTP, Country, UserContact, Company, CompanyUser, UserProfile, UnsubscribedNumber, Config
    import re
    from datetime import date, datetime, timedelta

    logger.info("in UserContactRegistrationTask Start")

    dtnow = datetime.now()
    onedayagotime = dtnow - timedelta(days=1)

    countryObj = Country.objects.get(pk=1)

    nosmsuserids = UserProfile.objects.filter(send_sms_to_contacts=False).values_list('user', flat=True)
    nosmsuserids_query = ""
    if len(nosmsuserids) > 0:
        nosmsuserids = map(str, nosmsuserids)
        nosmsuserids = ", ".join(nosmsuserids)
        nosmsuserids_query = "and api_usercontact.user_id not in ("+nosmsuserids+")"

    # ~ ucrawqueryset = UserContact.objects.raw("select id, name, number from api_usercontact where name REGEXP 'retail|shop|Vastra|Saree|saari|saaree|kurti|lehenga|Lahenga|lehnga|lahnga|blouse|suit|agent|adhat|dalal|fashion|fasion|fashon|feshon|feshion|ethnic|ethanic|ethnik|textile|txtl|textl|market|markt|Online|resaler|Reseller|reseler|agenc' and created > '"+str(onedayagotime.strftime("%Y-%m-%d %H:%M:%S"))+"' "+nosmsuserids_query+" group by number order by id")
    USER_CONTACT_REGEX = Config.objects.get(key="USER_CONTACT_REGEX").value
    from django.db import connection
    #query = "select api_usercontact.id, api_usercontact.name, api_usercontact.number from api_usercontact join api_companyuser on api_companyuser.user_id=api_usercontact.user_id join api_company on api_company.id=api_companyuser.company_id where api_usercontact.name REGEXP 'retail|shop|Vastra|Saree|saari|saaree|kurti|lehenga|Lahenga|lehnga|lahnga|blouse|suit|agent|adhat|dalal|fashion|fasion|fashon|feshon|feshion|ethnic|ethanic|ethnik|textile|txtl|textl|market|markt|Online|resaler|Reseller|reseler|agenc' and api_usercontact.name not like '%wishbook%' and api_company.name not like '%wishbook%' and created > '"+str(onedayagotime.strftime("%Y-%m-%d %H:%M:%S"))+"' "+nosmsuserids_query+" group by api_usercontact.number order by api_usercontact.id"
    query = "select api_usercontact.id, api_usercontact.name, api_usercontact.number from api_usercontact join api_companyuser on api_companyuser.user_id=api_usercontact.user_id join api_company on api_company.id=api_companyuser.company_id where api_usercontact.name REGEXP '" + USER_CONTACT_REGEX +"' and api_usercontact.name not like '%wishbook%' and api_company.name not like '%wishbook%' and api_usercontact.created > '"+str(onedayagotime.strftime("%Y-%m-%d %H:%M:%S"))+"' "+nosmsuserids_query+" group by api_usercontact.number order by api_usercontact.id"
    print query
    cursor = connection.cursor()
    cursor.execute(query)

    #print ucrawqueryset.query
    #for ucrawquery in ucrawqueryset:
    for ucrawquery in cursor.fetchall():
        number = ucrawquery[2]
        original_number = ucrawquery[2]
        number = re.sub('[^0-9+]', '',number)
        number = str(number)[-10:]
        name = ucrawquery[1]
        logger.info("number = %s, id = %s"% (str(number), str(ucrawquery[0])))

        if len(str(number)) < 5:
            error = "phone number is not valid. integer length should be more than 5"
            logger.info("raise error = %s, id = %s"% (str(error), str(ucrawquery[0])))
            continue

        if int(number[0]) in [0,1,2,3,4,5]:
            error = "phone number is not valid. should start from 6-9"
            logger.info("raise error = %s, id = %s"% (str(error), str(ucrawquery[0])))
            continue

        compnumber = getCompanyNumberFromNumber(countryObj, number)
        country = compnumber[0]
        phone_number = compnumber[1]

        if (not Company.objects.filter(country=country, phone_number=phone_number).exists() or UserProfile.objects.filter(phone_number=number, country=countryObj, user__last_login__isnull=True).exists()) and UnsubscribedNumber.objects.filter(country=country, phone_number=phone_number).exists() == False:
            datajson = {"country":1, "phone_number":number, "company_name":name}

            otp = None
            if not Company.objects.filter(country=country, phone_number=phone_number).exists() and not UserProfile.objects.filter(country=countryObj, phone_number=phone_number).exists():
                print "common_user_registration=========================="
                jsonres = common_user_registration(datajson, None, "return_otp")
                otp = jsonres["otp"]
            else:
                userprofile = UserProfile.objects.filter(phone_number=number, country=countryObj, user__last_login__isnull=True).first()
                print userprofile
                if userprofile:
                    print "UserProfile====getLastOTP=========================="
                    otp = getLastOTP(userprofile)
                else:
                    print "continue=================="
                    continue

            smsurl = 'https://app.wishbooks.io/?m='+str(phone_number)+'&o='+str(otp)+'&c='+str(country.id)+'&utm_source=sms&utm_medium=usercontact'
            smsurl = urlShortener(smsurl)




            userids = UserContact.objects.filter(number=original_number).values_list('user', flat=True)
            #print userids
            company_names = CompanyUser.objects.filter(user__in=userids, company__is_profile_set=True).values_list('company__name', flat=True)
            #print company_names

            final_number = str(country.phone_code)+str(phone_number)

            if len(company_names) > 0:
                userObj = CompanyUser.objects.filter(user__in=userids, company__is_profile_set=True).last()
                #print userObj.user
                print userObj.user.userprofile.language.name

                company_names_str = ", ".join(company_names[:2])
                namelen = len(company_names) - 2

                if userObj.user.userprofile.language.name == "Hindi":
                    if namelen > 0:
                        company_names_str = company_names_str+" aur "+str(namelen)+" vyapari"
                    company_names_str = company_names_str.encode('utf-8')
                    message = company_names_str+" apna textile business badha rahe hai Wishbook B2B App se. Aap bhi judiye! Download kijiye - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Mobile browser - "+smsurl

                    print message
                    smsSend([final_number], message, True)

                else:
                    if namelen > 0:
                        company_names_str = company_names_str+" & "+str(namelen)+" others"
                    company_names_str = company_names_str.encode('utf-8')
                    message = company_names_str+" are on Wishbook B2B app to grow their textile business. Why don't you join? Download Wishbook - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Also mobile browser - "+smsurl

                    print message
                    smsSend([final_number], message, True)

            else:
                userObj = UserContact.objects.filter(number=original_number).last()
                #print userObj.user
                print userObj.user.userprofile.language.name

                if userObj.user.userprofile.language.name == "Hindi":
                    print "is_profile_set = false, number =",number
                    message = "apna textile business badhane ke liye Wishbook B2B App se judiye!. Download kijiye - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Mobile browser - "+smsurl

                    print message
                    smsSend([final_number], message, True)
                else:
                    print "is_profile_set = false, number =",number
                    message = "Use Wishbook B2B app to grow your textile business. Download Wishbook - Android - www.wishbooks.io/android iOS - www.wishbooks.io/ios Also Mobile browser - "+smsurl

                    print message
                    smsSend([final_number], message, True)

            smsTrasaction("user_contact_task", 1)


    logger.info("in UserContactRegistrationTask Done")


@task()
def InActiveUserNotificationTask(userlogintime="before7to30days"):
    from api.common_functions import smsSend, urlShortener, getLastOTP, smsTemplates

    from datetime import date, datetime, timedelta
    from api.models import Catalog, Language, UnsubscribedNumber
    import random

    logger.info("in InActiveUserNotificationTask Start")
    logger.info("in InActiveUserNotificationTask userlogintime type = %s" % (userlogintime))

    #deeplinksmsurl = "http://app.wishbooks.io/?type=catalog&ctype=public"
    #deeplinksmsurl = urlShortener(deeplinksmsurl)

    unsubscribed_number = UnsubscribedNumber.objects.all().values_list('phone_number', flat=True).distinct()

    todayDate = date.today()

    before7DaysDate = todayDate - timedelta(days=7)
    before30DaysDate = todayDate - timedelta(days=30)

    total_catalogs = Catalog.objects.filter(view_permission="public", created_at__gte=before7DaysDate).count()

    rno = random.randrange(100000, 999999, 1)

    finalusers = []
    if userlogintime == "before7to30days":
        finalusers = User.objects.filter(last_login__lt=before7DaysDate, last_login__gt=before30DaysDate).exclude(is_staff=True).values_list('id', flat=True)
    elif userlogintime == "before30days":
        finalusers = User.objects.filter(Q(last_login__lt=before30DaysDate) | Q(last_login__isnull=True)).exclude(is_staff=True).values_list('id', flat=True)

    logger.info("in InActiveUserNotificationTask finalusers len = %s, array = %s" % (len(finalusers), finalusers))

    language = Language.objects.filter(name="English").first()

    message = str(total_catalogs)+"+ catalogs were uploaded last week. Did you see them? Check them out now! Let us know if you face any problem while browsing."

    #users = User.objects.filter(Q(Q(last_login__lt=before7DaysDate) | Q(last_login__isnull=True)) & Q(userprofile__language=language)).values_list('id', flat=True)
    users = User.objects.filter(id__in=finalusers, userprofile__language=language).values_list('id', flat=True)

    logger.info("in InActiveUserNotificationTask English notification users len = %s, array = %s" % (len(users), users))

    if settings.TASK_QUEUE_METHOD == 'celery':
        notificationSend.apply_async((users, message, {"notId":rno, "push_type":"inactive_user", "title":"Check New Catalogs", "other_para":{"not_action_1":"catalog_view", "not_action_2":"support_chat"} }), expires=datetime.now() + timedelta(days=2))
    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        task_id = async(
            'api.tasks.notificationSend',
            users, message, {"notId":rno, "push_type":"inactive_user", "title":"Check New Catalogs", "other_para":{"not_action_1":"catalog_view", "not_action_2":"support_chat"} }
        )

    #users = User.objects.filter(Q(Q(last_login__lt=before7DaysDate) | Q(last_login__isnull=True)) & Q(userprofile__language=language)).exclude(userprofile__phone_number__in=unsubscribed_number).order_by('id')
    users = User.objects.filter(id__in=users).exclude(userprofile__phone_number__in=unsubscribed_number).order_by('id')

    logger.info("in InActiveUserNotificationTask English sms users len = %s, array = %s" % (len(users), users))

    for user in users:
        smsurl = "www.wishbooks.io/android"
        if user.userprofile.last_login_platform == "Android":
            #smsurl = deeplinksmsurl
            otp = getLastOTP(user.userprofile)
            smsurl = 'https://app.wishbooks.io/?m='+str(user.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(user.userprofile.country.id)+'&utm_source=sms&utm_medium=inactive&type=catalog&ctype=public'
            smsurl = urlShortener(smsurl)

        template = smsTemplates("inactive_user_english")% (total_catalogs, smsurl)
        final_number = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
        if user.last_login is None:
            logger.info("in_queue smsSendTextNationPromotional")
            if settings.TASK_QUEUE_METHOD == 'celery':
                smsSendTextNationPromotional.apply_async(([final_number], template, True), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.smsSendTextNationPromotional',
                    [final_number], template, True
                )
        else:
            smsSend([final_number], template)

        smsTrasaction("inactive_user_task", 1)


    language = Language.objects.filter(name="Hindi").first()
    message = str(total_catalogs)+"+ catalogs upload hue the last week. Aapne dekhe kya? Abhi dekhiye! Kuch problem ho to hum se poochiye."

    #users = User.objects.filter(Q(Q(last_login__lt=before7DaysDate) | Q(last_login__isnull=True)) & Q(userprofile__language=language)).values_list('id', flat=True)
    users = User.objects.filter(id__in=finalusers, userprofile__language=language).values_list('id', flat=True)

    logger.info("in InActiveUserNotificationTask Hindi notification users len = %s, array = %s" % (len(users), users))

    if settings.TASK_QUEUE_METHOD == 'celery':
        notificationSend.apply_async((users, message, {"notId":rno, "push_type":"inactive_user", "title":"Check New Catalogs", "other_para":{"not_action_1":"catalog_view", "not_action_2":"support_chat"} }), expires=datetime.now() + timedelta(days=2))
    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        task_id = async(
            'api.tasks.notificationSend',
            users, message, {"notId":rno, "push_type":"inactive_user", "title":"Check New Catalogs", "other_para":{"not_action_1":"catalog_view", "not_action_2":"support_chat"} }
        )

    #users = User.objects.filter(Q(Q(last_login__lt=before7DaysDate) | Q(last_login__isnull=True)) & Q(userprofile__language=language)).exclude(userprofile__phone_number__in=unsubscribed_number).order_by('id')
    users = User.objects.filter(id__in=users).exclude(userprofile__phone_number__in=unsubscribed_number).order_by('id')

    logger.info("in InActiveUserNotificationTask Hindi sms users len = %s, array = %s" % (len(users), users))

    for user in users:
        smsurl = "www.wishbooks.io/android"
        if user.userprofile.last_login_platform == "Android":
            #smsurl = deeplinksmsurl
            otp = getLastOTP(user.userprofile)
            smsurl = 'https://app.wishbooks.io/?m='+str(user.userprofile.phone_number)+'&o='+str(otp)+'&c='+str(user.userprofile.country.id)+'&utm_source=sms&utm_medium=inactive&type=catalog&ctype=public'
            smsurl = urlShortener(smsurl)

        template = smsTemplates("inactive_user_hindi")% (total_catalogs, smsurl)
        final_number = str(user.userprofile.country.phone_code)+str(user.userprofile.phone_number)
        if user.last_login is None:
            logger.info("in_queue smsSendTextNationPromotional")
            if settings.TASK_QUEUE_METHOD == 'celery':
                smsSendTextNationPromotional.apply_async(([final_number], template, True), expires=datetime.now() + timedelta(days=2))
            elif settings.TASK_QUEUE_METHOD == 'djangoQ':
                task_id = async(
                    'api.tasks.smsSendTextNationPromotional',
                    [final_number], template, True
                )
        else:
            smsSend([final_number], template)

        smsTrasaction("inactive_user_task", 1)

    logger.info("in InActiveUserNotificationTask End")


@task()
def MobileStateMappingTask():
    from datetime import date, datetime, timedelta
    from api.models import MobileStateMapping, Address, State

    logger.info("in MobileStateMapping Start")

    nostate = State.objects.filter(state_name="-").first()

    addressObjs = Address.objects.filter(state=nostate , user__isnull=False).order_by('id')

    for addressObj in addressObjs:
        print "addressObj =",addressObj.id
        number_start_with = addressObj.user.userprofile.phone_number[:4]
        print "number_start_with =",number_start_with
        msmObj = MobileStateMapping.objects.filter(mobile_no_start_with=number_start_with).first()
        if msmObj:
            print "msmObj", msmObj
            addressObj.state = msmObj.state
            addressObj.save()


    logger.info("in MobileStateMapping End")

@task()
def skuMapCSVImportJobs(job_id):
    logger.info("skuMapCSVImportJobs task job_id = %s"% (job_id))
    from api.models import *

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone

    logger.info("skuMapCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

    logger.info("skuMapCSVImportJobs 222 ====")

    err = ""

    errorfilename = 'jobs_error_file/skumap_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['wishbook_sku', 'external_sku', 'wishbook_catalog', 'external_catalog', 'error']

    column = 1
    rows = 0
    fields = {}

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                #with transaction.atomic():
                for fields in reader:
                    column += 1

                    logger.info(str(fields))

                    product_sku = fields['wishbook_sku']
                    mapped_sku = fields['external_sku']
                    catalog_title = fields['wishbook_catalog']
                    mapped_catalog = fields['external_catalog']

                    if product_sku == "" and catalog_title == "":
                        logger.info("Enter SKU or Catalog")
                        err = {"skumap_csv":"Enter SKU or Catalog"}
                        #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'Enter SKU or Catalog'])
                        fields["error"] = err["skumap_csv"]
                        writer.writerow(fields)
                        continue

                    if catalog_title == "": #product_sku != "" and
                        logger.info("Enter Catalog")
                        err = {"skumap_csv":"Enter Catalog"}
                        #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'Enter SKU or Catalog'])
                        fields["error"] = err["skumap_csv"]
                        writer.writerow(fields)
                        continue

                    if product_sku != "" and mapped_sku.strip() == "":
                        logger.info("Enter Mapped SKU")
                        err = {"skumap_csv":"Enter Mapped SKU"}
                        fields["error"] = err["skumap_csv"]
                        writer.writerow(fields)
                        continue

                    sellingCompanyObj = Buyer.objects.filter(buying_company=loginCompany, status="approved").values_list('selling_company', flat=True).distinct()

                    catalogId = CompanyProductFlat.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).values_list('catalog', flat=True).distinct()
                    catalogId = list(catalogId)
                    companyPublicCatlogId = Catalog.objects.filter(company=loginCompany).values_list('id', flat=True).distinct() #Q(view_permission__icontains='public') | Q(company=loginCompany)
                    catalogId.extend(list(companyPublicCatlogId))
                    publicCatlogId = CatalogSeller.objects.filter(selling_company=loginCompany, selling_type="Public").values_list('catalog', flat=True).distinct()
                    catalogId.extend(list(publicCatlogId))
                    print "catalogId", catalogId

                    catalogObj = Catalog.objects.filter(id__in=catalogId, title__iexact=catalog_title).last()
                    if catalogObj:
                        if mapped_catalog is not None and mapped_catalog.strip() != "":
                            if SKUMap.objects.filter(external_catalog__iexact = mapped_catalog, app_instance = appInstanceObj).exclude(catalog=catalogObj, app_instance = appInstanceObj).exists():
                                err = {"skumap_csv":"External Catalog already exists : "+mapped_catalog}
                                #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'External catalog already exists'])
                                fields["error"] = err["skumap_csv"]
                                writer.writerow(fields)
                                continue
                            # ~ if SKUMap.objects.filter(catalog=catalogObj, app_instance = appInstanceObj).exists():
                                # ~ SKUMap.objects.filter(catalog=catalogObj, app_instance = appInstanceObj).update(external_catalog = mapped_catalog)
                            # ~ else:
                                # ~ SKUMap.objects.create(catalog=catalogObj, app_instance = appInstanceObj, external_catalog = mapped_catalog)
                            if not SKUMap.objects.filter(catalog=catalogObj, app_instance = appInstanceObj, external_catalog = mapped_catalog).exists():
                                SKUMap.objects.create(catalog=catalogObj, app_instance = appInstanceObj, external_catalog = mapped_catalog)
                    else:
                        err = {"skumap_csv":"Enter a valid wishbook catalog : "+catalog_title}
                        #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'Enter a valid wishbook catalog'])
                        fields["error"] = err["skumap_csv"]
                        writer.writerow(fields)
                        continue



                    if product_sku != "":
                        # ~ pushUserProductId = CompanyProductFlat.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).order_by('product').values_list('product', flat=True).distinct()
                        # ~ companyAndPublicCatlogId = Catalog.objects.filter(company=loginCompany).values_list('id', flat=True).distinct()#Q(view_permission__icontains='public') | Q(company=loginCompany)

                        # ~ if not Product.objects.filter(Q(sku__iexact=product_sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).exists():
                        if not Product.objects.filter(sku__iexact=product_sku, catalog=catalogObj).exists():
                            logger.info("Enter a valid wishbook_sku")
                            err = {"skumap_csv":"Enter a valid wishbook sku : "+product_sku}
                            #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'Enter valid wishbook sku'])
                            fields["error"] = err["skumap_csv"]
                            writer.writerow(fields)
                            continue

                        # ~ if Product.objects.filter(Q(sku__iexact=product_sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).count() > 1:
                        if Product.objects.filter(sku__iexact=product_sku, catalog=catalogObj).count() > 1:
                            logger.info("Same wishbook_sku exists multiple times")
                            err = {"skumap_csv":"Same wishbook sku exists multiple times : "+product_sku}
                            #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'Same wishbook sku exists multiple times'])
                            fields["error"] = err["skumap_csv"]
                            writer.writerow(fields)
                            continue

                        # ~ productObj = Product.objects.filter(Q(sku__iexact=product_sku) & (Q(catalog__in=companyAndPublicCatlogId) | Q(id__in=pushUserProductId))).last()
                        productObj = Product.objects.filter(sku__iexact=product_sku, catalog=catalogObj).last()

                        if SKUMap.objects.filter(external_sku__iexact=mapped_sku, app_instance = appInstanceObj).exclude(product=productObj, app_instance = appInstanceObj).exists():
                            err = {"skumap_csv":"External SKU already exists : "+mapped_sku}
                            #writer.writerow([product_sku, mapped_sku, catalog_title, mapped_catalog, 'External sku already exists'])
                            fields["error"] = err["skumap_csv"]
                            writer.writerow(fields)
                            continue
                        # ~ if SKUMap.objects.filter(product=productObj, app_instance = appInstanceObj).exists():
                            # ~ SKUMap.objects.filter(product=productObj, app_instance = appInstanceObj).update(external_sku = mapped_sku)
                        # ~ else:
                            # ~ SKUMap.objects.create(product=productObj, app_instance = appInstanceObj, external_sku = mapped_sku)
                        if not SKUMap.objects.filter(product=productObj, app_instance = appInstanceObj, external_sku = mapped_sku).exists():
                            SKUMap.objects.create(product=productObj, app_instance = appInstanceObj, external_sku = mapped_sku)

                    #if catalog_title != "":


                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()


            except Exception as e:
                logger.info("skuMapCSVImportJobs start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True



@task()
def companyMapCSVImportJobs(job_id):
    logger.info("companyMapCSVImportJobs task job_id = %s"% (job_id))
    from api.models import *

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone

    logger.info("companyMapCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

    logger.info("companyMapCSVImportJobs 222 ====")

    err = ""

    errorfilename = 'jobs_error_file/companymap_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['wishbook_company', 'external_company', 'error']

    column = 1
    rows = 0
    fields = {}

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                #with transaction.atomic():
                for fields in reader:
                    column += 1

                    logger.info(str(fields))

                    buyer_company_name = fields['wishbook_company']
                    mapped_company_name = fields['external_company']

                    if buyer_company_name == "" or mapped_company_name == "":
                        err = {"companymap_csv":"Enter Wishbook Company Name and External Company Name"}
                        logger.info(err)
                        #writer.writerow([buyer_company_name, mapped_company_name, 'Enter Wishbook Company Name and External Company Name'])
                        fields["error"] = err["companymap_csv"]
                        writer.writerow(fields)
                        continue

                    buyingCompanyObj = None
                    #buyerObj = Buyer.objects.filter(selling_company=loginCompany, status="approved", buying_company__name__iexact=buyer_company_name).last()
                    buyerObj = Buyer.objects.filter(Q(selling_company=loginCompany, status="approved") & Q( Q(buying_company__name__iexact=buyer_company_name) | Q(buying_company_name__iexact=buyer_company_name) | Q(buying_person_name__iexact=buyer_company_name) )).last()
                    if buyerObj:
                        buyingCompanyObj = buyerObj.buying_company
                    print buyingCompanyObj
                    #CompanyAccount.objects.create(company=loginCompany, buyer_company=buyingCompanyObj, mapped_accout_ref=mapped_company_name)

                    if buyingCompanyObj:
                        if CompanyAccount.objects.filter(company=loginCompany, mapped_accout_ref__iexact=mapped_company_name).exists():
                            err = {"companymap_csv":"External Company Name already exists : "+mapped_company_name}
                            #writer.writerow([buyer_company_name, mapped_company_name, 'External Company Name already exists'])
                            fields["error"] = err["companymap_csv"]
                            writer.writerow(fields)
                            continue
                        if CompanyAccount.objects.filter(company=loginCompany, buyer_company=buyingCompanyObj).exists():
                            CompanyAccount.objects.filter(company=loginCompany, buyer_company=buyingCompanyObj).update(mapped_accout_ref = mapped_company_name)
                        else:
                            CompanyAccount.objects.create(company=loginCompany, buyer_company=buyingCompanyObj, mapped_accout_ref=mapped_company_name)
                    else:
                        err = {"companymap_csv":"Wishbook Company Name is not found: "+buyer_company_name}
                        logger.info(err)
                        #writer.writerow([buyer_company_name, mapped_company_name, 'Wishbook Company Name is not found'])
                        fields["error"] = err["companymap_csv"]
                        writer.writerow(fields)
                        continue

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()


            except Exception as e:
                logger.info("companyMapCSVImportJobs start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True

@task()
def shipmentCSVImportJobs(job_id, auto_generate_order = True):
    logger.info("shipmentCSVImportJobs task job_id = %s"% (job_id))
    from api.models import *

    from api.v1.serializers import InvoiceSerializer
    from api.v1.views import InvoiceViewSet

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone
    from dateutil.parser import parse
    from datetime import date, datetime, timedelta

    logger.info("shipmentCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

    logger.info("shipmentCSVImportJobs 222 ====")

    err = ""
    error_found = ""

    foldername = 'jobs_error_file/wishbook_invoice'+str(job_id)+'_'+str(randomString())
    folderpath = os.path.join(settings.MEDIA_ROOT, foldername)
    os.makedirs(folderpath)

    #errorfilename = 'jobs_error_file/invoice_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilename = foldername+'/invoice_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['invoice_number', 'order_number', 'buyer_name', 'buyer_number', 'gst', 'pan', 'catalog', 'sku', 'qty', 'rate', 'discount', 'hsn_code', 'amount', 'packing_type', 'invoice_date', 'error_or_success'] #'logistics_partner', 'logistic_tracking_number', 'dispatch_date',


    sellingCompanyObj = Buyer.objects.filter(buying_company=loginCompany, status="approved").values_list('selling_company', flat=True).distinct()
    catalogsIds = Push_User.objects.filter(buying_company=loginCompany, selling_company__in=sellingCompanyObj).exclude(catalog__isnull=True).order_by('-push').values_list('catalog', flat=True).distinct()
    catalogsIds = list(catalogsIds)
    catalogObjs = Catalog.objects.filter(Q(company=loginCompany) | Q(id__in=catalogsIds)) # | Q(view_permission="public")

    last_invoice_number = None
    last_order_id = None
    lastSalesorderObj = None
    error_salesorder_ids = [] #error invoice number stores

    salesorder_ids = [] #not using
    products = []
    invoices = []
    error_csv_data = []

    invoice_number_arr = []

    create_order_csvdata = []
    order_number_not_match_err = "Order number is not matched"


    column = 1
    rows = 0
    fields = {}

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                #with transaction.atomic():
                for fields in reader:
                    if err != "":
                        error_found = err
                    err = ""

                    column += 1

                    logger.info("shipmentCSVImportJobs start line in loop = %s"% (fields))

                    #order_id = fields['order_id']
                    invoice_number = fields['invoice_number']
                    order_number = fields['order_number']

                    buyer_name = fields['buyer_name']
                    buyer_number = fields['buyer_number']
                    gst = fields['gst']
                    pan = fields['pan']
                    qty = fields['qty']
                    rate = fields['rate']
                    discount = fields['discount']
                    if "-" in discount:
                        discount = discount.replace("-", "")
                    print "final  discount=", discount
                    hsn_code = fields['hsn_code']
                    amount = fields['amount']

                    catalog = fields['catalog']
                    sku = fields['sku']
                    if sku:
						if sku == "0" or sku==0:
							sku = ""

                    #qty = int(fields['qty'])
                    # print "qty original }}}}}}}}}}}}}}}}}}}}}}}}}}}}", fields['qty']
                    # qty = int(fields['qty'].split(".")[0])
                    # print "qty int }}}}}}}}}}}}}}}}}}}}}}}}}}}}", qty
                    #rate = Decimal(fields['rate'])
                    #amount = fields['amount']

                    invoice_date = fields['invoice_date']
                    # ~ dispatch_date = fields['dispatch_date']

                    packing_type = fields.get('packing_type', "") #fields['packing_type']

                    # ~ logistics_partner = fields['logistics_partner']
                    # ~ logistic_tracking_number = fields['logistic_tracking_number']

                    order_required_on_new_invice_err = False
                    if last_invoice_number != invoice_number and last_invoice_number is not None and invoice_number != "" and order_number == "":
                        lastSalesorderObj = None
                        order_required_on_new_invice_err = True
                        #continue;

                    logger.info("last_invoice_number = %s"% (str(last_invoice_number)))
                    if invoice_number == "" and last_invoice_number is None:
                        err = "Invoice number is required"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    if invoice_number == "":
                        invoice_number = last_invoice_number
                    logger.info("invoice_number = %s"% (str(invoice_number)))

                    if Invoice.objects.filter(order__seller_company=loginCompany, invoice_number=invoice_number).exists():
                        last_invoice_number = invoice_number
                        err = "Invoice number already exists. Please choose another"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    if invoice_number not in invoice_number_arr:
                        invoice_number_arr.append(invoice_number)
                        products.append([])
                        invoices.append([])
                        error_csv_data.append([])
                    salesorder_index = invoice_number_arr.index(invoice_number)


                    if invoice_number != last_invoice_number:
                        inv_json = {"invoice_number":invoice_number, "order":None}
                        if invoice_date != "":
                            inv_json["datetime"] = invoice_date
                        invoices[salesorder_index] = inv_json

                    if discount != "" and discount is not None:
                        logger.info("discount_from_csv = %s"% (discount))
                        invoices[salesorder_index]["discount_from_csv"] = discount

                    # ~ last_order_id = salesOrderObj.id
                    last_invoice_number = invoice_number

                    # if invoice_number in error_salesorder_ids:
                    #     fields["error_or_success"] = ""
                    #     writer.writerow(fields)
                    #     continue;

                    if order_required_on_new_invice_err:
                        err = "Order number is required on new invoice number"
                        fields["error_or_success"] = err
                        error_csv_data[salesorder_index].append(fields)
                        error_salesorder_ids.append(invoice_number)
                        continue;



                    print "lastSalesorderObj------",lastSalesorderObj
                    if order_number == "" and lastSalesorderObj is None: #order_id == "" and
                        #err = "Order number or Order ID is required"
                        lastSalesorderObj = None
                        err = "Order number is required"
                        #writer.writerow([str(invoice_number), str(order_number), str(catalog), str(sku), str(qty), str(packing_type), str(logistics_partner), str(logistic_tracking_number), err])
                        fields["error_or_success"] = err
                        # writer.writerow(fields)
                        # if invoice_number != "":
                        #     error_salesorder_ids.append(invoice_number)
                        error_salesorder_ids.append(invoice_number)
                        error_csv_data[salesorder_index].append(fields)

                        create_order_csvdata.append(fields)
                        continue;

                    salesOrderObj = None
                    logger.info("lastSalesorderObj = %s"% (str(lastSalesorderObj)))
                    #if order_id != "":
                    #	salesOrderObj = SalesOrder.objects.filter(seller_company=loginCompany, id=order_id).order_by('-id').first()
                    if order_number != "":# and salesOrderObj is None:
                        logger.info("if order_number != :")
                        salesOrderObj = SalesOrder.objects.filter(seller_company=loginCompany, order_number=order_number).order_by('-id').first()
                        if salesOrderObj is None:
                            lastSalesorderObj = None
                            err = order_number_not_match_err
                            fields["error_or_success"] = err
                            # writer.writerow(fields)
                            error_salesorder_ids.append(invoice_number)
                            error_csv_data[salesorder_index].append(fields)

                            create_order_csvdata.append(fields)
                            continue;
                    if salesOrderObj is None and lastSalesorderObj is not None:
                        logger.info("if salesOrderObj is None and lastSalesorderObj is not None:")
                        salesOrderObj = lastSalesorderObj
                    '''if invoice_number != "" and salesOrderObj is None:
                        iObj = Invoice.objects.filter(invoice_number=invoice_number).order_by('-id').first()
                        if iObj:
                            salesOrderObj = iObj.order'''

                    logger.info("salesOrderObj = %s"% (str(salesOrderObj)))

                    if salesOrderObj is None:
                        lastSalesorderObj = None
                        err = order_number_not_match_err
                        #writer.writerow([str(invoice_number), str(order_number), str(catalog), str(sku), str(qty), str(packing_type), str(logistics_partner), str(logistic_tracking_number), err])
                        fields["error_or_success"] = err
                        # writer.writerow(fields)
                        error_salesorder_ids.append(invoice_number)
                        error_csv_data[salesorder_index].append(fields)

                        create_order_csvdata.append(fields)
                        continue;

                    try:
                        logger.info("qty original = %s" % (qty))
                        qty = int(qty.split(".")[0])
                        logger.info("qty final = %s" % (qty))

                        logger.info("rate original = %s" % (rate))
                        rate = Decimal(rate)
                        logger.info("rate final = %s" % (rate))
                    except Exception as e:
                        logger.info("Qty and Rate Exception = %s" % (e))
                        err = "Please check Qty and Rate and both are required"
                        fields["error_or_success"] = err
                        error_salesorder_ids.append(invoice_number)
                        error_csv_data[salesorder_index].append(fields)
                        continue;

                    # if discount != "" and discount is not None:
                    #     print "seller_extra_discount_percentage save "
                    #     salesOrderObj.seller_extra_discount_percentage = discount
                    #     salesOrderObj.save()






                    # ~ if salesOrderObj.id not in salesorder_ids:
                        # ~ salesorder_ids.append(salesOrderObj.id)
                        # ~ products.append([])
                        # ~ invoices.append([])
                        # ~ error_csv_data.append([])
                    # ~ salesorder_index = salesorder_ids.index(salesOrderObj.id)


                    # ~ if salesOrderObj.id != last_order_id:
                        # ~ inv_json = {"order":salesOrderObj.id, "invoice_number":invoice_number}
                        # ~ if invoice_date != "":
                            # ~ inv_json["datetime"] = invoice_date
                        # ~ invoices[salesorder_index] = inv_json

                    # ~ last_order_id = salesOrderObj.id
                    # ~ lastSalesorderObj = salesOrderObj

                    if invoices[salesorder_index]["order"] is None:
                        invoices[salesorder_index]["order"] = salesOrderObj.id
                    elif invoices[salesorder_index]["order"] != salesOrderObj.id:
                        err = "Multi order number found in single invoice"
                        fields["error_or_success"] = err
                        error_salesorder_ids.append(invoice_number)
                        error_csv_data[salesorder_index].append(fields)
                        continue;






                    lastSalesorderObj = salesOrderObj


                    if salesOrderObj.processing_status == "Dispatched":
                        err = "Order is dispatched already"
                        #writer.writerow([str(invoice_number), str(order_number), str(catalog), str(sku), str(qty), str(packing_type), str(logistics_partner), str(logistic_tracking_number), err])
                        fields["error_or_success"] = err
                        # writer.writerow(fields)
                        error_salesorder_ids.append(invoice_number)
                        error_csv_data[salesorder_index].append(fields)
                        continue;

                    #err = ""

                    if catalog == "" and sku == "":
                        err = "Catalog or SKU is required"
                        # ~ error_salesorder_ids.append(salesOrderObj.id)
                        error_salesorder_ids.append(invoice_number)
                        #error_csv_data[salesorder_index].append([str(invoice_number), str(order_number), str(catalog), str(sku), str(qty), str(packing_type), str(logistics_partner), str(logistic_tracking_number), err])
                        fields["error_or_success"] = err
                        error_csv_data[salesorder_index].append(fields)
                        continue;

                    #catalogObj = catalogObjs.filter(title=catalog).last()
                    #logger.info("catalogObj = %s"% (str(catalogObj)))

                    #if catalogObj is None or salesOrderObj.items.filter(product__catalog=catalogObj).exists() == False:

                    #full_dispatch = True
                    #invoiceitem_set = []
                    total_qty = 0
                    total_amount = 0




                    aiObj = AppInstance.objects.filter(company=loginCompany).last()

                    if sku == "":
                        catalogObj = None
                        if aiObj:
                            skumapObj=SKUMap.objects.filter(external_catalog__iexact=catalog, app_instance=aiObj).last()
                            if skumapObj:
                                catalogObj = skumapObj.catalog
                        if catalogObj is None:
                            catalogObj = catalogObjs.filter(title__iexact=catalog).last()

                        logger.info("catalogObj = %s"% (str(catalogObj)))
                        if catalogObj is None:
                            err = "Catalog not found"
                            error_salesorder_ids.append(invoice_number)
                            fields["error_or_success"] = err
                            error_csv_data[salesorder_index].append(fields)
                            continue;

                        if salesOrderObj.items.filter(product__catalog=catalogObj).exists() == False:
                            #add catalog in order
                            # ~ err = "Catalog not matched for this order"
                            # ~ error_salesorder_ids.append(invoice_number)
                            # ~ fields["error_or_success"] = err
                            # ~ error_csv_data[salesorder_index].append(fields)
                            # ~ continue;

                            '''
                            totalproducts = catalogObj.products.count()
                            designwiseqty = float(qty)/ totalproducts

                            logger.info("designwiseqty = %s"% (str(designwiseqty)))
                            if (qty % totalproducts) > 0:
                                err = "Qty should be the multiple of "+str(totalproducts)+" (no. of designs in this catalog)"
                                error_salesorder_ids.append(invoice_number)
                                fields["error_or_success"] = err
                                error_csv_data[salesorder_index].append(fields)
                                continue;
                            '''

                            items = catalogObj.products.all()

                            if items.count() == 0:
                                err = "Catalog has no products"
                                error_salesorder_ids.append(invoice_number)
                                fields["error_or_success"] = err
                                error_csv_data[salesorder_index].append(fields)
                                continue;

                            design_wise_qty = get_design_wise_qty(items, qty)
                            logger.info("design_wise_qty = %s"% (str(design_wise_qty)))
                            items = design_wise_qty["items"]
                            dispatch_ind_qty = design_wise_qty["dispatch_ind_qty"]

                            #for productObj in catalogObj.products.all():
                            idx = 0
                            approximate_order = False
                            for productObj in items:
                                designwisedispatchqty = dispatch_ind_qty[idx]
                                idx = idx + 1
                                if designwisedispatchqty > 0:
                                    approximate_order = True
                                    if not SalesOrderItem.objects.filter(product=productObj, sales_order = salesOrderObj).exists():
                                        salesitem = SalesOrderItem.objects.get_or_create(product=productObj, quantity=designwisedispatchqty, rate=rate, sales_order=salesOrderObj, pending_quantity=designwisedispatchqty, packing_type=packing_type)
                                        print "salesitem ))))))))))))))))))))))) ",salesitem

                            if approximate_order == True:
                                salesOrderObj.approximate_order = True
                                salesOrderObj.save()

                        #catalogObj = salesOrderObj.items.filter(product__catalog__title=catalog).first().product.catalog
                        #logger.info("catalogObj = %s"% (str(catalogObj)))

                        #items = salesOrderObj.items.filter(product__catalog=catalogObj)
                        #items = salesOrderObj.items.filter(product__catalog__title=catalog)
                        if packing_type != "":
                            items = salesOrderObj.items.filter(product__catalog=catalogObj, packing_type=packing_type)
                            if items.count() == 0:#not found any packing_type
                                items = salesOrderObj.items.filter(product__catalog=catalogObj)
                        else:
                            items = salesOrderObj.items.filter(product__catalog=catalogObj)
                        #designwisedispatchqty = totalproducts / qty
                        print "..........items===",items



                        '''
                        #totalproducts = salesOrderObj.items.all().count()
                        totalproducts = items.count()

                        # ~ totalPenQty = items.aggregate(Sum('pending_quantity')).get('pending_quantity__sum', 0)
                        # ~ if totalPenQty is None:
                            # ~ totalPenQty = 0
                        # ~ logger.info("totalPenQty = %s"% (str(totalPenQty)))
                        # ~ if totalPenQty == 0:
                            # ~ err = "Order has no pending quantity"
                            # ~ error_salesorder_ids.append(invoice_number)
                            # ~ fields["error_or_success"] = err
                            # ~ error_csv_data[salesorder_index].append(fields)
                            # ~ continue;

                        logger.info("qty = %s"% (str(qty)))
                        logger.info("totalproducts = %s"% (str(totalproducts)))

                        design_to_decrease_by = 0
                        if (qty % totalproducts) > 0:
                            design_to_decrease_by = 1
                            if (qty % (totalproducts - design_to_decrease_by)) > 0:
                                design_to_decrease_by = 2
                                if (qty % (totalproducts - design_to_decrease_by)) > 0:
                                    design_to_decrease_by = 0
                                    # ~ err = "Qty should be the multiple of "+str(totalproducts)+" (no. of designs in this catalog)"
                                    # ~ error_salesorder_ids.append(invoice_number)
                                    # ~ fields["error_or_success"] = err
                                    # ~ error_csv_data[salesorder_index].append(fields)
                                    # ~ continue;

                        items = items[:totalproducts - design_to_decrease_by]

                        #items has been changes so new count will apply
                        totalproducts = items.count()

                        # ~ designwisedispatchqty = int(qty)/ totalproducts
                        # ~ logger.info("designwisedispatchqty = %s"% (str(designwisedispatchqty)))

                        dispatch_ind_qty = []
                        for idx in range(totalproducts):
                            dispatch_ind_qty.append(0)
                        dividable_qty = qty
                        while (dividable_qty > 0):
                            for idx in range(totalproducts):
                                if dividable_qty > 0:
                                    dispatch_ind_qty[idx] = dispatch_ind_qty[idx] + 1
                                    dividable_qty = dividable_qty - 1

                        logger.info("dispatch_ind_qty = %s"% (dispatch_ind_qty))
                        '''

                        design_wise_qty = get_design_wise_qty(items, qty)
                        logger.info("design_wise_qty = %s"% (str(design_wise_qty)))
                        items = design_wise_qty["items"]
                        dispatch_ind_qty = design_wise_qty["dispatch_ind_qty"]

                        logger.info("final items to loop = %s"% (str(items)))
                        idx = 0
                        for item in items:
                            logger.info("pending_quantity = %s"% (str(item.pending_quantity)))
                            designwisedispatchqty = dispatch_ind_qty[idx]
                            idx = idx + 1
                            logger.info("designwisedispatchqty = %s"% (str(designwisedispatchqty)))

                            if designwisedispatchqty > 0:
                                if designwisedispatchqty > item.pending_quantity:
                                    item.pending_quantity = designwisedispatchqty
                                    item.quantity = item.quantity + (designwisedispatchqty - item.pending_quantity)
                                    item.save()
                                    # ~ err = "Number of designs not matched. should not be more than "+str(totalPenQty)
                                    # ~ continue;

                                    #err = "Number of designs not matched. should not be more than "+str(item.pending_quantity)
                                    #error_salesorder_ids.append(salesOrderObj.id)
                                    #error_csv_data[salesorder_index].append([str(invoice_number), str(order_id), str(order_number), str(catalog), str(sku), str(qty), str(rate), str(amount), str(logistics_partner), str(logistic_tracking_number), err])


                                #if qty != item.quantity:
                                #	full_dispatch = False
                                total_qty += designwisedispatchqty
                                total_amount += designwisedispatchqty * item.rate
                                #invoiceitem_set.append({"order_item":item.id, "qty":qty})
                                products[salesorder_index].append({"order_item":item.id, "qty":designwisedispatchqty})


                    else:
                        product = None
                        #aiObj = AppInstance.objects.filter(company=loginCompany).last()
                        if aiObj:
                            skumapObj=SKUMap.objects.filter(external_sku__iexact=sku, app_instance=aiObj).last()
                            if skumapObj:
                                product = skumapObj.product

                        if product is None:
                            #product = catalogObj.products.filter(sku=sku).last()
                            product = Product.objects.filter(catalog__in=catalogObjs, sku__iexact=sku).last()


                        logger.info("product = %s"% (str(product)))
                        if product is None:
                            err = "SKU not found"
                            error_salesorder_ids.append(invoice_number)
                            fields["error_or_success"] = err
                            error_csv_data[salesorder_index].append(fields)
                            continue;

                        if salesOrderObj.items.filter(product=product).exists() == False:
                            salesitem = SalesOrderItem.objects.get_or_create(product=product, quantity=qty, rate=rate, sales_order=salesOrderObj, pending_quantity=qty, packing_type=packing_type)
                            print "salesitem ))))))))))))))))))))))) ",salesitem
                            salesOrderObj.approximate_order = True
                            salesOrderObj.save()

                        #items = salesOrderObj.items.filter(product=product, packing_type=packing_type)
                        if packing_type != "":
                            items = salesOrderObj.items.filter(product=product, packing_type=packing_type)
                            if items.count() == 0:#not found any packing_type
                                items = salesOrderObj.items.filter(product=product)
                        else:
                            items = salesOrderObj.items.filter(product=product)

                        #designwisedispatchqty = qty
                        for item in items:
                            logger.info("pending_quantity = %s"% (str(item.pending_quantity)))
                            if qty > item.pending_quantity:
                                item.pending_quantity = qty
                                item.quantity = item.quantity + (qty - item.pending_quantity)
                                item.save()

                                # ~ err = "Number of designs not matched. should not be more than "+str(item.pending_quantity)
                                #error_salesorder_ids.append(salesOrderObj.id)
                                #error_csv_data[salesorder_index].append([str(invoice_number), str(order_id), str(order_number), str(catalog), str(sku), str(qty), str(rate), str(amount), str(logistics_partner), str(logistic_tracking_number), err])
                                # ~ continue;

                            #if qty != item.quantity:
                            #	full_dispatch = False
                            total_qty += qty
                            total_amount += qty * item.rate
                            #invoiceitem_set.append({"order_item":item.id, "qty":qty})
                            products[salesorder_index].append({"order_item":item.id, "qty":qty})

                    logger.info("item products = %s"% (str(products)))
                    #logger.info("full_dispatch = %s"% (str(full_dispatch)))
                    #logger.info("invoiceitem_set = %s"% (str(invoiceitem_set)))

                    if err != "":
                        logger.info("if err = %s"% (str(err)))
                        # ~ error_salesorder_ids.append(salesOrderObj.id)
                        error_salesorder_ids.append(invoice_number)
                    #error_csv_data[salesorder_index].append([str(invoice_number), str(order_number), str(catalog), str(sku), str(qty), str(packing_type), str(logistics_partner), str(logistic_tracking_number), err])
                    fields["error_or_success"] = err
                    error_csv_data[salesorder_index].append(fields)

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()


            except Exception as e:
                logger.info("shipmentCSVImportJobs Exception = 1, start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                #jobsObj.exception_details = str(e)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                jobsObj.save()
                pass


            logger.info("invoice_number_arr === %s"% (str(invoice_number_arr)))
            # ~ logger.info("salesorder_ids === %s"% (str(salesorder_ids)))
            logger.info("products === %s"% (str(products)))
            logger.info("invoices === %s"% (str(invoices)))
            logger.info("error_salesorder_ids === %s"% (str(error_salesorder_ids)))
            logger.info("error_csv_data === %s"% (str(error_csv_data)))

            # ~ for idx, buyer_id in enumerate(salesorder_ids):
            for idx, buyer_id in enumerate(invoice_number_arr):
                try:
                    jsondata = invoices[idx]
                    logger.info("jsondata with invoices === %s"% (str(jsondata)))
                    if jsondata['invoice_number'] in error_salesorder_ids:
                        err = "something wrong"
                        for esi in error_csv_data[idx]:
                            writer.writerow(esi)
                        continue

                    jsondata['invoiceitem_set'] = products[idx]
                    jsondata['created_from_csv'] = True

                    logger.info("jsondata full === %s"% (str(jsondata)))

                    # ~ if jsondata['order'] in error_salesorder_ids:

                    invoice = InvoiceSerializer(data=jsondata)#, context={'request': request}
                    if invoice.is_valid():
                        logger.info("save is_valid invoice")
                        inObj = invoice.save()

                        if "datetime" in invoices[idx].keys():
                            #inObj.datetime = parse(invoices[idx]["datetime"])
                            #inObj.datetime = datetime.strptime(invoices[idx]["datetime"], "%d/%m/%Y").strftime('%Y-%m-%d')
                            inObj.datetime = datetime.strptime(invoices[idx]["datetime"], "%d/%m/%Y").strftime('%Y-%m-%d %H:%M:%S')
                            inObj.save()

                        #ivs = InvoiceViewSet(pk=inObj.id)

                        #to change request data
                        # ~ mutable = request.data._mutable
                        # ~ request.data._mutable = True
                        # ~ request.data['tracking_number'] = logistic_tracking_number
                        # ~ request.data['logistics_provider'] = logistics_partner
                        # ~ if dispatch_date != "":
                            # ~ request.data['dispatch_date'] = dispatch_date
                        # ~ request.data._mutable = mutable
                        # ~ ivs.dispatched(request, inObj.id)

                        #below code was final
                        # ~ request = {}
                        # ~ request["data"] = {}
                        # ~ request["data"]['tracking_number'] = logistic_tracking_number
                        # ~ request["data"]['logistics_provider'] = logistics_partner
                        # ~ if dispatch_date != "":
                            # ~ request["data"]['dispatch_date'] = parse(dispatch_date)
                        # ~ ivs.dispatched(request, inObj.id)

                    else:
                        err = invoice.errors.values()
                        logger.info("invoice.errors === %s"% (str(err)))
                        print err
                except Exception as e:
                    logger.info("shipmentCSVImportJobs Exception = 2, start error = %s"% (str(e)))
                    err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                    jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                    import traceback
                    jobsObj.exception_details = "Exception = 2, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                    jobsObj.save()
                    pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()


    if len(create_order_csvdata) > 0 and auto_generate_order is True:
        logger.info("create_order_csvdata_path start====")
        #create_order_csvdata_filename = 'jobs_upload_file/sales_order_error_'+str(job_id)+'_'+str(randomString())+'.csv'
        create_order_csvdata_filename = foldername+'/new_sales_order_import_'+str(job_id)+'_'+str(randomString())+'.csv'
        create_order_csvdata_path = os.path.join(settings.MEDIA_ROOT, create_order_csvdata_filename)
        fieldnames = ['order_number', 'buyer_name', 'buyer_number', 'catalog', 'sku', 'qty', 'rate', 'packing_type', 'item_remark', 'order_remark', 'broker_number', 'date', 'gst', 'pan', 'state', 'city', 'error_or_success']

        with open(create_order_csvdata_path, "wb") as out_filesc:
            writer = csv.DictWriter(out_filesc, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()
            try:
                for errorcsv in create_order_csvdata:
                    errorjson = {}
                    errorjson["order_number"] = errorcsv["order_number"]
                    errorjson["buyer_name"] = errorcsv["buyer_name"]
                    errorjson["buyer_number"] = errorcsv["buyer_number"]
                    errorjson["catalog"] = errorcsv["catalog"]
                    errorjson["sku"] = errorcsv["sku"]
                    errorjson["qty"] = errorcsv["qty"]
                    errorjson["rate"] = errorcsv["rate"]
                    errorjson["packing_type"] = errorcsv["packing_type"]
                    errorjson["item_remark"] = ""
                    errorjson["order_remark"] = ""
                    errorjson["broker_number"] = ""
                    errorjson["date"] = errorcsv["invoice_date"]
                    errorjson["gst"] = errorcsv["gst"]
                    errorjson["pan"] = errorcsv["pan"]
                    errorjson["state"] = ""
                    errorjson["city"] = ""


                    writer.writerow(errorjson)
            except Exception as e:
                import traceback
                print "create_order_csvdata_path Exception =", traceback.format_exc()
                pass

        # newJobsObj = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Sales Order CSV", upload_file=create_order_csvdata_filename, status="Scheduled", start_time = timezone.now(), total_rows=len(create_order_csvdata))

        logger.info("create_order_csvdata_path done====")
        logger.info(create_order_csvdata_path)



        logger.info("create_invoice_path start====")
        #create_invoice_filename = 'jobs_upload_file/invoice_error_'+str(job_id)+'_'+str(randomString())+'.csv'
        create_invoice_filename = foldername+'/new_invoice_import_'+str(job_id)+'_'+str(randomString())+'.csv'
        create_invoice_path = os.path.join(settings.MEDIA_ROOT, create_invoice_filename)
        fieldnames = ['invoice_number', 'order_number', 'buyer_name', 'buyer_number', 'gst', 'pan', 'catalog', 'sku', 'qty', 'rate', 'discount', 'hsn_code', 'amount', 'packing_type', 'invoice_date', 'error_or_success']

        with open(create_invoice_path, "wb") as out_filesc:
            writer = csv.DictWriter(out_filesc, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()
            try:
                for errorcsv in create_order_csvdata:
                    writer.writerow(errorcsv)
            except Exception as e:
                import traceback
                print "create_invoice_path Exception =", traceback.format_exc()
                pass

        # newJobsObjShipmentSO = Jobs.objects.create(user=loginUser, company=loginCompany, job_type="Shipment Sales Order CSV", upload_file=create_invoice_filename, status="Created", start_time = timezone.now(), total_rows=len(create_order_csvdata))

        logger.info("create_invoice_path done====")
        logger.info(create_invoice_path)


        # newJobsObj.action_note=newJobsObjShipmentSO.id
        # newJobsObj.save()
        #
        # if settings.TASK_QUEUE_METHOD == 'celery':
        #     task_id = salesOrderCSVImportJobs.apply_async((newJobsObj.id,), expires=datetime.now() + timedelta(days=2))
        # elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        #     task_id = async(
        #         'api.tasks.salesOrderCSVImportJobs',
        #         newJobsObj.id,
        #         broker = priority_broker
        #     )
        # logger.info("create_order_csvdata_path salesOrderCSVImportJobs task_id=")
        # logger.info(str(task_id))





    if err != "" or error_found != "":
        try:
            logger.info("shipmentCSVImportJobs err = %s, error_found = %s" %(err, error_found))

            import shutil
            zipres = shutil.make_archive(folderpath, "zip", folderpath)
            print zipres

            if wrong_csv_uploaded is False:
                #jobsObj.error_file=errorfilename
                jobsObj.error_file=foldername+".zip"
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True


@task()
def SellerStatisticTask():
    from datetime import date, datetime, timedelta
    from api.models import SellerStatistic, Company, Catalog, CompanyUser, CatalogSeller, Buyer, SalesOrder, Product, Invoice
    from api.common_functions import getDisableCatalogIds
    from django.db.models import Sum
    from api.admin import SellerStatisticResource


    logger.info("in SellerStatisticTask Start")

    todayDate = date.today()
    last30dayDate = todayDate - timedelta(days=30)
    last30dayCatalogSellerDate = last30dayDate + timedelta(days=45)#from company

    print todayDate, last30dayDate, last30dayCatalogSellerDate

    companies = Catalog.objects.filter(created_at__gte=last30dayDate).values_list('company', flat=True)
    companies = list(companies)
    cscompanies = CatalogSeller.objects.filter(selling_type="Public", expiry_date__gte=last30dayCatalogSellerDate).values_list('selling_company', flat=True)
    companies.extend(list(cscompanies))

    companies = Company.objects.filter(id__in=companies).order_by('id')

    #companies = Company.objects.filter(id__in=[245,253])

    for company in companies:
        print "company =",company

        last30dayCatalogSellerDate = last30dayDate + timedelta(days=company.default_catalog_lifetime)

        ssObj, created = SellerStatistic.objects.get_or_create(company=company)
        ssObj.name = company.name
        ssObj.wishbook_salesman = company.wishbook_salesman

        ct = company.company_group_flag
        arr = []
        if ct.manufacturer is True:
            arr.append('Manufacturer')
        if ct.wholesaler_distributor is True:
            arr.append('Wholesaler Distributor')
        if ct.retailer is True:
            arr.append('Retailer')
        if ct.online_retailer_reseller is True:
            arr.append('Online Retailer Reseller')
        if ct.broker is True:
            arr.append('Broker')

        ssObj.company_type = ", ".join(arr)
        if company.address:
            ssObj.city = company.address.city.city_name
        elif company.city:
            ssObj.city = company.city.city_name
        ssObj.phone_number = company.phone_number

        cuObj = CompanyUser.objects.filter(company=company).first()
        if cuObj:
            ssObj.last_login = cuObj.user.last_login


        last_30days_catalogs = Catalog.objects.filter(company=company, created_at__gte=last30dayDate).order_by('id')
        last_30days_catalog_sellers = CatalogSeller.objects.filter(selling_company=company, selling_type="Public", expiry_date__gte=last30dayCatalogSellerDate).exclude(catalog__company=company).order_by('id')

        disableCatalogIds = getDisableCatalogIds(company)

        allcatalogids = last_30days_catalogs.values_list('id', flat=True)
        allcatalogids = list(allcatalogids)
        allcatalogsellerids = last_30days_catalog_sellers.values_list('catalog__id', flat=True)
        allcatalogids.extend(list(allcatalogsellerids))



        # ~ catalogtitlearr = last_30days_catalogs.values_list('title', flat=True)
        # ~ catalogtitlearr = list(catalogtitlearr)
        # ~ catalogsellertitlearr = last_30days_catalog_sellers.values_list('catalog__title', flat=True)
        # ~ catalogtitlearr.extend(list(catalogsellertitlearr))
        # ~ ssObj.catalogs_uploaded = ", ".join(catalogtitlearr)
        ssObj.catalogs_uploaded = last_30days_catalogs.count()

        # ~ total_mycatalog_seller = last_30days_catalogs.count()
        # ~ total_mycatalog_seller = total_mycatalog_seller + last_30days_catalog_sellers.count()
        # ~ ssObj.total_catalog_seller = total_mycatalog_seller
        ssObj.total_catalog_seller = last_30days_catalog_sellers.count()

        ssObj.total_enabled_catalog = Catalog.objects.filter(id__in=allcatalogids).exclude(id__in=disableCatalogIds).count()

        l30c = last_30days_catalogs.last()
        l30cs = last_30days_catalog_sellers.last()
        if l30c:
            ssObj.last_catalog_upload_date = l30c.created_at
            ssObj.last_catalog_or_seller_name = l30c.title

        if l30cs:
            ssObj.last_catalog_seller_date = l30cs.expiry_date.date() - timedelta(days=45)
            ssObj.last_catalog_or_seller_name = l30cs.catalog.title

        if l30c and l30cs:
            if ssObj.last_catalog_upload_date > ssObj.last_catalog_seller_date:
                ssObj.last_catalog_or_seller_name = l30c.title
            else:
                ssObj.last_catalog_or_seller_name = l30cs.catalog.title


        ssObj.total_enquiry_received = Buyer.objects.filter(selling_company=company, created_type="Enquiry", created_at__gte=last30dayDate).count()
        ssObj.total_enquiry_converted = Buyer.objects.filter(selling_company=company, created_type="Enquiry", created_at__gte=last30dayDate, buyer_type="Relationship").count()
        ssObj.total_enquiry_pending = Buyer.objects.filter(selling_company=company, created_type="Enquiry", created_at__gte=last30dayDate, buyer_type="Enquiry").count()
        enq_cat_ids = Buyer.objects.filter(selling_company=company, created_type="Enquiry", created_at__gte=last30dayDate, enquiry_catalog__isnull=False).values_list('enquiry_catalog', flat=True)
        total_enquiry_values = Product.objects.filter(catalog__in=enq_cat_ids).aggregate(Sum('public_price')).get('public_price__sum', 0)
        if total_enquiry_values is None:
			total_enquiry_values = 0
        ssObj.total_enquiry_values = total_enquiry_values
        #ssObj.handling_time = handling_time


        salesorderids = SalesOrder.objects.filter(seller_company=company, created_at__gte=last30dayDate).exclude(processing_status__in=["Cart", "Draft"]).values_list('id', flat=True)

        total_order_values = Invoice.objects.filter(order__in=salesorderids).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
        if total_order_values is None:
			total_order_values = 0
        ssObj.total_order_values = total_order_values


        salesorderids = SalesOrder.objects.filter(seller_company=company, created_at__gte=last30dayDate, processing_status__in=["Pending","ordered","Accepted","In Progress"]).values_list('id', flat=True)

        total_pending_order_values = Invoice.objects.filter(order__in=salesorderids).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
        if total_pending_order_values is None:
			total_pending_order_values = 0
        ssObj.total_pending_order_values = total_pending_order_values
        ssObj.total_pending_order = salesorderids.count()

        #for prepaid orders
        from django.db import connection
        prepaid_query = "SELECT group_concat(id) as ids FROM `api_salesorder` WHERE `seller_company_id`="+str(company.id)+" and (`payment_date` < `dispatch_date` or (payment_date is not null and dispatch_date is null)) order by id desc"
        cursor = connection.cursor()
        cursor.execute( prepaid_query )
        row = cursor.fetchone()

        print row

        prepaidids = []
        if row[0]:
            prepaidids = row[0].split(',')


        salesorderids = SalesOrder.objects.filter(seller_company=company, created_at__gte=last30dayDate, id__in=prepaidids).values_list('id', flat=True)

        total_prepaid_order_values = Invoice.objects.filter(order__in=salesorderids, payment_status__in=["Paid", "Success"]).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
        if total_prepaid_order_values is None:
			total_prepaid_order_values = 0
        ssObj.total_prepaid_order_values = total_prepaid_order_values

        total_prepaid_cancelled_order_values = Invoice.objects.filter(order__in=salesorderids, payment_status__in=["Paid", "Success"], status="Cancelled").aggregate(Sum('total_amount')).get('total_amount__sum', 0)
        if total_prepaid_cancelled_order_values is None:
			total_prepaid_cancelled_order_values = 0
        ssObj.total_prepaid_cancelled_order_values = total_prepaid_cancelled_order_values
        #ssObj.avg_dispatch_time = avg_dispatch_time

        cancel_salesorderids = SalesOrder.objects.filter(seller_company=company, created_at__gte=last30dayDate, id__in=prepaidids, processing_status__in=["Cancelled","Transferred"]).values_list('id', flat=True)

        ssObj.enquiry_not_handled = ssObj.total_enquiry_pending

        if salesorderids.count() > 0 and cancel_salesorderids.count() > 0:
            ssObj.prepaid_order_cancellation_rate = (cancel_salesorderids.count()/salesorderids.count())*100






        ssObj.save()


    dataset = SellerStatisticResource().export()
    #print dataset.csv

    mail = EmailMessage("Seller Statistics CSV", "Please find the attached for seller statistics data", "tech@wishbook.io", ["tech@wishbook.io", "arvind@wishbook.io", "ankur@wishbook.io", "deepikad@wishbook.io"])
    mail.attach("seller_statistics.csv", dataset.csv, "text/csv")
    mail.send()


    logger.info("in SellerStatisticTask End")

@task()
def UserCampaignClickTask():
    from datetime import date, datetime, timedelta
    from django.db.models import Sum, Min, Max, Count
    from api.models import UserCampaignClick
    from api.admin import UserCampaignClickResource


    logger.info("in UserCampaignClickTask Start")

    clicks_maxids = UserCampaignClick.objects.all().values('user', 'campaign').annotate(Max('id')).values('id__max')

    queryset = UserCampaignClick.objects.filter(id__in=clicks_maxids)
    dataset = UserCampaignClickResource().export(queryset)
    #print dataset.csv

    mail = EmailMessage("User Campaign Clicks CSV", "Please find the attached for user campaign data", "tech@wishbook.io", ["tech@wishbook.io", "deepikad@wishbook.io", "jigar@wishbook.io", "aayushik@wishbook.io"])
    mail.attach("user_campaign_clicks.csv", dataset.csv, "text/csv")
    mail.send()

    logger.info("in UserCampaignClickTask End")


@task()
def MeetingCSVeMailTask():
	from datetime import date, datetime, timedelta
	from django.db.models import Sum, Min, Max, Count
	from api.models import Meeting
	from api.admin import MeetingResource


	logger.info("in MeetingCSVeMailTask Start")

	todayDate = datetime.now()
	lastDate = todayDate - timedelta(days=30)

	queryset = Meeting.objects.filter(start_datetime__gte=lastDate)
	dataset = MeetingResource().export(queryset)
	#print dataset.csv

	mail = EmailMessage("Meetings CSV", "Please find the attached for meetings", "tech@wishbook.io", ["tech@wishbook.io", "arvind@wishbook.io", "hr@wishbook.io", "ankur@wishbook.io"])
	#mail = EmailMessage("Meetings CSV", "Please find the attached for meetings", "tech@wishbook.io", ["tech@wishbook.io"])
	mail.attach("meetings.csv", dataset.csv, "text/csv")
	mail.send()

	logger.info("in MeetingCSVeMailTask End")


@task()
def catalogCSVImportJobs(job_id):
    logger.info("catalogCSVImportJobs task job_id = %s"% (job_id))
    from api.models import Catalog, CatalogSeller, Product, Jobs, Brand, BrandDistributor, Category, AppInstance, SKUMap

    #from api.v1.serializers import InvoiceSerializer
    #from api.v1.views import InvoiceViewSet

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone
    from dateutil.parser import parse

    logger.info("catalogCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    logger.info("catalogCSVImportJobs 222 ====")

    err = ""

    errorfilename = 'jobs_error_file/catalog_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['title', 'brand_name', 'category_name', 'sell_full_catalog', 'map_external_catalog', 'error']


    brand_distributor = BrandDistributor.objects.filter(company=loginCompany).order_by('brand').values_list('brand', flat=True).distinct()
    brands = Brand.objects.filter(Q(company=loginCompany) | Q(id__in=brand_distributor)).distinct()

    categories = Category.objects.filter(parent_category=10)

    appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

    column = 1
    rows = 0
    fields = {}

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                for fields in reader:
                    column += 1

                    logger.info(str(fields))

                    title = fields['title']
                    brand_name = fields['brand_name']
                    # ~ view_permission = fields['view_permission']
                    category_name = fields['category_name']
                    sell_full_catalog = fields['sell_full_catalog']
                    mapped_catalog = fields['map_external_catalog']

                    if Catalog.objects.filter(title=title, company=loginCompany).exists():
                        err = "Catalog already exists with the same title. Please change the title"
                        fields["error"] = err
                        writer.writerow(fields)
                        continue;

                    brandObj = brands.filter(name=brand_name).first()
                    if brandObj is None:
                        err = "Brand name is not Found"
                        fields["error"] = err
                        writer.writerow(fields)
                        continue;

                    # ~ view_permission = view_permission.lower()
                    # ~ if view_permission in ["private"]:
                        # ~ view_permission = "push"

                    categoryObj = categories.filter(category_name=category_name).first()
                    if categoryObj is None:
                        err = "Category name is not Found"
                        fields["error"] = err
                        writer.writerow(fields)
                        continue;

                    if sell_full_catalog.lower() == "true":
                        sell_full_catalog = True
                    else:
                        sell_full_catalog = False

                    catalogObj = Catalog.objects.create(title=title, brand=brandObj, view_permission="push", category=categoryObj, sell_full_catalog=sell_full_catalog, company=loginCompany, user=loginUser, thumbnail="logo-single.png")

                    if mapped_catalog is not None and mapped_catalog.strip() != "":
                        if SKUMap.objects.filter(external_catalog__iexact = mapped_catalog, app_instance = appInstanceObj).exists():
                            err = "Catalog is not mapped as external Catalog already exists"
                            fields["error"] = err
                            writer.writerow(fields)
                            continue
                        SKUMap.objects.create(catalog=catalogObj, app_instance = appInstanceObj, external_catalog = mapped_catalog)

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()


            except Exception as e:
                logger.info("catalogCSVImportJobs start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                #jobsObj.exception_details = str(e)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True



@task()
def catalogBulkCSVImportJobs(job_id):
    logger.info("task job_id = %s"% (job_id))
    import os
    import io
    import csv
    from django.conf import settings
    from django.utils import timezone
    import datetime
    from api.models import (
        Catalog,Company,
        CatalogSeller,
        Product, Jobs,
        Brand, BrandDistributor,
        Category, AppInstance,
    )
    from api.common_functions import handel_catalog_eav
    from api.v1.views import randomString

    jobsObj             = Jobs.objects.get(pk=job_id)
    jobsObj.status      = 'In Progress'
    jobsObj.start_time  = timezone.now()
    jobsObj.save()

    loginUser       = jobsObj.user
    loginCompany    = jobsObj.company
    companyName     = loginCompany.name
    decoded_file    = jobsObj.upload_file.read().decode('utf-8')
    io_string       = io.StringIO(decoded_file)
    reader          = csv.DictReader(io_string)
    data            = [r for r in reader]
    if len(data) == 0:
        jobsObj.status      = 'Completed'
        jobsObj.error_details = "Empty CSV File!"
        jobsObj.save()
        return True

    err_check = False
    err = ""
    errorfilename = 'jobs_error_file/catalog_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['Company',
        'Brand',
    	'Catalog Name',
        'Product Type',
        'Fabric',
        'Work',
        'Style',
        'Other',
        'Stitching Type',
    	'Available Sizes',
    	'Number of Designs',
    	'Images Folder',
    	'Cover Image',
    	'Per design price',
    	'Single pcs available',
        'Single pcs Extra Amount',
        'Single pcs Extra Percentage',
        'Dispatch date',
        'Availability duration',
        'View Permission',
        'error'
    ]
    column  = 1
    rows    = 0
    csv_headers         = reader.fieldnames
    wrong_csv_uploaded  = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                try:
                    column += 1
                    logger.info("csv row Catalog data === %s " %(str(row)))
                    for key in row:
                        row[key] = row[key].strip()
                    if not row['Catalog Name']:
                        err_check = True
                        handle_csv_error('Catalog Name',writer,row)
                        continue
                    if not row['Brand']:
                        err_check = True
                        handle_csv_error('Brand ID',writer,row)
                        continue

                    eav_data = {}
                    if not row['Fabric']:
                        err_check = True
                        handle_csv_error('Fabric',writer,row)
                        continue

                    eav_data["fabric"] = strip_csv(row['Fabric'].split(','))

                    if not row['Work']:
                        err_check = True
                        handle_csv_error('Work',writer,row)
                        continue

                    eav_data["work"] = strip_csv(row['Work'].split(','))

                    if row['Style']:
                        eav_data["style"] = row['Style'].split(',')[0]
                    if not row['Number of Designs']:
                        err_check = True
                        handle_csv_error('Number of Designs',writer,row)
                        continue
                    if not row['Per design price']:
                        err_check = True
                        handle_csv_error('Per design price',writer,row)
                        continue
                    if not row['Single pcs available']:
                        err_check = True
                        handle_csv_error('Single pcs available',writer,row)
                        continue
                    if row['Single pcs available'].lower() == 'true':
                        if not (row['Single pcs Extra Amount'] or row['Single pcs Extra Percentage']):
                            err_check = True
                            handle_csv_error('Single pcs Extra/Single pcs Extra Percentage',writer,row)
                            continue

                        if row['Single pcs Extra Amount']:
                            row['Single pcs Extra Amount']  =   float(row['Single pcs Extra Amount'])

                        if row['Single pcs Extra Percentage']:
                            row['Single pcs Extra Percentage']  = float(row['Single pcs Extra Percentage'])

                        sell_full_catalog   = False
                    else:
                        sell_full_catalog                    = True
                        row['Single pcs Extra Amount']       = None
                        row['Single pcs Extra Percentage']   = None



                    eav_data["number_pcs_design_per_set"] 	 = row['Number of Designs']
                    eav_data["stitching_type"]               = row['Stitching Type']
                    eav_data["other"]                        = row['Other']

                    categories      = Category.objects.filter(parent_category=10)
                    loginCompany    = Company.objects.filter(id=row['Company']).first()
                    if loginCompany is None:
                        err_check = True
                        err = "Company with id %s " % row['Company']
                        handle_csv_error(err,writer,row)
                        continue
                    companyName  = loginCompany.name
                    if Catalog.objects.filter(title__iexact=row['Catalog Name'], company=loginCompany).exists():
                        err_check = True
                        err = "Catalog with this name already exists."
                        handle_csv_error('',writer,row,err)
                        continue

                    categoryObj = categories.filter(category_name__iexact=row['Product Type']).first()
                    if categoryObj is None:
                        err_check = True
                        handle_csv_error('Product Type',writer,row)
                        continue
                    brand_distributor  = BrandDistributor.objects.filter(company=loginCompany).order_by('brand').values_list('brand', flat=True).distinct()
                    brands             = Brand.objects.filter(Q(company=loginCompany) | Q(id__in=brand_distributor)).distinct()
                    brandObj           = brands.filter(id=row['Brand']).first()
                    if brandObj is None:
                        err_check = True
                        err = "Error with your Brand : Brand is Not owned or Sell By You"
                        handle_csv_error('',writer,row,err)
                        continue
                    if row['Available Sizes']:
                        eav_data["size"] = strip_csv(row['Available Sizes'].split(','))
                    if row['Dispatch date']:
                        dispatch_date	=  datetime.datetime.strptime(row['Dispatch date'], '%d-%m-%Y')
                    else:
                        dispatch_date 	= datetime.datetime.today()
                    if row['Availability duration']:
                        expiry_date = datetime.datetime.today() +  datetime.timedelta(int(row['Availability duration']))
                    else:
                        expiry_date = datetime.datetime.today() + datetime.timedelta(loginCompany.default_catalog_lifetime)
                    print "eav_data",eav_data
                    if row['Images Folder']:
                        folder_path =  row['Images Folder']
                        images_folder_path = os.path.join(settings.MEDIA_ROOT, row['Images Folder'])
                    else:
                        folder_path = row['Catalog Name'].lower() + '/'
                        images_folder_path = os.path.join(settings.MEDIA_ROOT, row['Catalog Name'].lower()) + '/'
                    if not row['Cover Image']:
                        err_check = True
                        handle_csv_error('Cover Image',writer,row)
                        continue

                    cover_image_path = folder_path + row['Cover Image']
                    image_list = os.listdir(images_folder_path)
                    if not (row['Cover Image'] in image_list):
                        err_check = True
                        err = "Cover image : %s is not found in %s" %(row['Cover Image'],folder_path)
                        handle_csv_error('',writer,row,err)
                        continue

                    image_list.remove(row['Cover Image'])
                    if len(image_list) != int(row['Number of Designs']):
                        err_check = True
                        err = "Number of designs mismatch found %s instead of %s" %(len(image_list),row['Number of Designs'])
                        handle_csv_error('',writer,row,err)
                        continue

                    catalog  = 	Catalog.objects.create(
                        title=row['Catalog Name'], brand=brandObj,
                        category=categoryObj,
                        view_permission=row['View Permission'],
                        sell_full_catalog=sell_full_catalog,
                        company=loginCompany,
                        user=loginUser,
                        thumbnail=cover_image_path,
                        dispatch_date=dispatch_date,
                        single_piece_price =row['Single pcs Extra Amount'],
                        single_piece_price_percentage=row['Single pcs Extra Percentage']

                    )

                    eav_err = handel_catalog_eav(catalog,eav_data)
                    if eav_err:
                        catalog.delete()
                        err_check = True
                        logger.info("eav error = %s " %(eav_err))
                        err = eav_err
                        handle_csv_error('',writer,row,err)
                        continue

                    for image_name in image_list:
                        image_path = folder_path + image_name
                        if '.' in image_name:
                            image_name = ('.').join(image_name.split('.')[:-1])

                        product  = 	Product.objects.create(
                            title=image_name[:29],
                            catalog=catalog,
                            sku=image_name[:29],
                            price=float(row['Per design price']),
                            public_price=float(row['Per design price']),
                            user=loginUser,
                            image=image_path
                        )

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()
                except Exception as e:
                    logger.error('Common Error:', exc_info=True)
                    err = "Error: %s" %(str(e))
                    err_check = True
                    handle_csv_error('',writer,row,err)
                    continue
    jobsObj.completed_rows  = rows
    jobsObj.status          = 'Completed'
    jobsObj.end_time        = timezone.now()
    jobsObj.save()

    if err_check:
        try:
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            logger.info("err = %s " %(str(err)))
            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.error("Exception " , exc_info=True)
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("successfull")
        except Exception as e:
            logger.error("Exception " , exc_info=True)
        return True

@task()
def productCSVImportJobs(job_id):
    logger.info("productCSVImportJobs task job_id = %s"% (job_id))
    from api.models import Catalog, CatalogSeller, Product, Jobs, Brand, BrandDistributor, Category, AppInstance, SKUMap

    #from api.v1.serializers import InvoiceSerializer
    #from api.v1.views import InvoiceViewSet

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone
    from dateutil.parser import parse

    logger.info("productCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    logger.info("productCSVImportJobs 222 ====")

    err = ""

    errorfilename = 'jobs_error_file/product_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)
    fieldnames = ['sku', 'price', 'wishbook_catalog_title', 'map_external_sku', 'error'] #'public_price',


    catalogs = Catalog.objects.filter(company=loginCompany, view_permission="push")

    appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

    column = 1
    rows = 0
    fields = {}

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                for fields in reader:
                    column += 1

                    logger.info(str(fields))

                    sku = title = fields['sku']
                    price = public_price = fields['price']
                    catalog_title = fields['wishbook_catalog_title']
                    mapped_sku = fields['map_external_sku']
                    #public_price = fields['public_price']

                    if not catalogs.filter(title=catalog_title).exists():
                        err = "Catalog is not exists"
                        if Catalog.objects.filter(company=loginCompany, view_permission="public").exists():
                            err = "Catalog must be private"
                        fields["error"] = err
                        writer.writerow(fields)
                        continue;

                    catalogObj = catalogs.filter(title=catalog_title).last()

                    if sku is not None and sku != "":
                        if Product.objects.filter(sku=sku, catalog__brand=catalogObj.brand, catalog__company=loginCompany).exclude(deleted=True).exists():
                            err = "sku should be unique"
                            fields["error"] = err
                            writer.writerow(fields)
                            continue;

                    # ~ if catalogObj.view_permission == "public":
                        # ~ if public_price is None or public_price <= 100:
                            # ~ err = "public price must be more than 100"
                            # ~ fields["error"] = err
                            # ~ writer.writerow(fields)
                            # ~ continue;

                    if price is None or price <= 100:
                        err = "public price must be more than 100"
                        fields["error"] = err
                        writer.writerow(fields)
                        continue;

                    productObj = Product.objects.create(title=title, catalog=catalogObj, sku=sku, price=price, public_price=public_price, user=loginUser, image="logo-single.png")

                    if mapped_sku is not None and mapped_sku.strip() != "":
                        if SKUMap.objects.filter(external_sku__iexact = mapped_sku, app_instance = appInstanceObj).exists():
                            err = "Product is not mapped as external SKU already exists"
                            fields["error"] = err
                            writer.writerow(fields)
                            continue
                        SKUMap.objects.create(product=productObj, app_instance = appInstanceObj, external_sku = mapped_sku)

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()


            except Exception as e:
                logger.info("productCSVImportJobs start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                #jobsObj.exception_details = str(e)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))
            #Jobs.objects.filter(id=job_id).update(error_file=errorfilename)
            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True



@task()
def shipmentDispatchCSVImportJobs(job_id):
    logger.info("shipmentDispatchCSVImportJobs task job_id = %s"% (job_id))
    from api.models import Jobs, AppInstance, SalesOrder, Invoice, Shipment, CompanyUser
    from django.contrib.auth.models import User

    from api.v1.serializers import InvoiceSerializer
    from api.v1.views import InvoiceViewSet

    from rest_framework.response import Response
    from django.http import HttpResponse
    import csv
    import re
    from rest_framework import serializers
    from django.conf import settings
    from os.path import join
    import os
    from api.v1.views import randomString
    import random
    from django.utils import timezone
    from dateutil.parser import parse
    from datetime import date, datetime, timedelta
    from api.common_functions import sendAllTypesMessage

    logger.info("shipmentDispatchCSVImportJobs 111")

    jobsObj = Jobs.objects.get(pk=job_id)
    jobsObj.status = 'In Progress'
    jobsObj.start_time = timezone.now()
    jobsObj.save()

    loginUser = jobsObj.user
    loginCompany = jobsObj.company
    companyName = loginCompany.name

    reader = csv.DictReader(jobsObj.upload_file)
    print "reader =",reader

    appInstanceObj = AppInstance.objects.filter(company=loginCompany).first()

    logger.info("shipmentDispatchCSVImportJobs 222 ====")

    err = ""

    errorfilename = 'jobs_error_file/shipment_error_'+str(job_id)+'_'+str(randomString())+'.csv'
    errorfilepath = os.path.join(settings.MEDIA_ROOT, errorfilename)

    fieldnames = ['invoice_number', 'order_number', 'logistics_partner', 'logistic_tracking_number', 'dispatch_date', 'error_or_success']

    column = 1
    rows = 0
    fields = {}

    invoice_order_number_done = []

    logger.info("shipmentDispatchCSVImportJobs 333 ====")

    csv_headers = reader.fieldnames
    print "csv_headers = ",csv_headers

    logger.info("shipmentDispatchCSVImportJobs 444 ====")

    wrong_csv_uploaded = False
    for csv_header in csv_headers:
        if csv_header not in fieldnames:
            wrong_csv_uploaded = True

    if wrong_csv_uploaded:
        err = {"csv":"Wrong CSV File Uploaded"}
        jobsObj.error_details = "Wrong CSV File Uploaded"
    else:
        with open(errorfilepath, "wb") as out_file:
            writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
            writer.writeheader()

            try:
                for fields in reader:
                    column += 1

                    logger.info(str(fields))

                    invoice_number = fields['invoice_number']
                    order_number = fields['order_number']

                    dispatch_date = fields['dispatch_date']
                    logistics_partner = fields['logistics_partner']
                    logistic_tracking_number = fields['logistic_tracking_number']

                    #if invoice_number == "" or order_number == "":
                    if invoice_number == "" and order_number == "":
                        err = "Invoice number and Order number are required"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    if [invoice_number,order_number] in invoice_order_number_done:
                        continue
                    else:
                        invoice_order_number_done.append([invoice_number,order_number])

                    if invoice_number == "":
                        err = "Invoice number is required"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    if order_number == "":
                        err = "Order number is required"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    salesOrderObj = None
                    invoiceObjs = None

                    if order_number != "":
                        salesOrderObj = SalesOrder.objects.filter(seller_company=loginCompany, order_number=order_number).order_by('-id').first()

                    logger.info("salesOrderObj = %s"% (str(salesOrderObj)))
                    if salesOrderObj is None:
                        err = "Sales Order not found"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    if invoice_number != "":
                        invoiceObjs = Invoice.objects.filter(order__seller_company=loginCompany, invoice_number=invoice_number, order=salesOrderObj).order_by('-id')#.first()
                        # ~ if salesOrderObj is None:
                            # ~ salesOrderObj = invoiceObj.order

                    logger.info("invoiceObjs = %s"% (str(invoiceObjs)))
                    if invoiceObjs is None:
                        err = "Invoice not found"
                        fields["error_or_success"] = err
                        writer.writerow(fields)
                        continue;

                    new_dispatch_date = None
                    if dispatch_date != "":
                        try:
                            new_dispatch_date = datetime.strptime(dispatch_date, "%d/%m/%Y").strftime('%Y-%m-%d')
                        except Exception as e:
                            err = "Change date format to dd/MM/YYYY"
                            fields["error_or_success"] = err
                            writer.writerow(fields)
                            continue;

                    for invoiceObj in invoiceObjs:
                        shipmentObj = Shipment.objects.filter(invoice=invoiceObj).last()
                        if shipmentObj:
							print "shipmentObj ==",shipmentObj
							shipmentObj.tracking_number = logistic_tracking_number
							shipmentObj.logistics_provider = logistics_partner
							if new_dispatch_date:
								shipmentObj.datetime = new_dispatch_date
							shipmentObj.save()

							jsonarr = {}
							jsonarr['order_number'] = invoiceObj.order.order_number
							jsonarr['table_id'] = invoiceObj.order.id
							jsonarr['status'] = invoiceObj.status #invoice.order.processing_status
							jsonarr['title'] = "Purchase Order "+str(invoiceObj.status)
							jsonarr['action'] = "update"

							broker_users = []
							if invoiceObj.order.broker_company is not None:
								broker_users=CompanyUser.objects.filter(company=invoiceObj.order.broker_company).values_list('user', flat=True).distinct()
							user1 = invoiceObj.order.company.company_users.values_list('user', flat=True)
							user1 = User.objects.filter(Q(id__in=user1) | Q(id__in=broker_users)).exclude(groups__name="salesperson") # | Q(id__in=deputed_users)
							#sendNotifications(user1, message, jsonarr)

							sendAllTypesMessage("shipment", user1, jsonarr)
                        else:
                            ivs = InvoiceViewSet(pk=invoiceObj.id)

                            request = {}
                            request["data"] = {}
                            request["data"]['tracking_number'] = logistic_tracking_number
                            request["data"]['logistics_provider'] = logistics_partner
                            if new_dispatch_date:
                                request["data"]['dispatch_date'] = datetime.strptime(dispatch_date, "%d/%m/%Y").strftime('%Y-%m-%d')

                            # if dispatch_date != "":
                            #     #request["data"]['dispatch_date'] = parse(dispatch_date)
                            #     try:
                            #         request["data"]['dispatch_date'] = datetime.strptime(dispatch_date, "%d/%m/%Y").strftime('%Y-%m-%d')
                            #     except Exception as e:
                            #         err = "Change date format to dd/MM/YYYY"
                            #         fields["error_or_success"] = err
                            #         writer.writerow(fields)
                            #         continue;

                            ivs.dispatched(request, invoiceObj.id)

                            logger.info("ivs = %s"% (str(ivs)))

                    rows += 1
                    jobsObj.completed_rows=rows
                    jobsObj.save()


            except Exception as e:
                logger.info("shipmentDispatchCSVImportJobs start error = %s"% (str(e)))
                err = {"csv":"Check csv file and found something wrong around row no = "+str(column)}

                jobsObj.error_details = "Check csv file and found something wrong around row no = "+str(column)
                #jobsObj.exception_details = str(e)
                import traceback
                jobsObj.exception_details = "Exception = 1, Fields = "+str(fields)+", Details = "+str(traceback.format_exc())
                pass

    jobsObj.completed_rows=rows
    jobsObj.status = 'Completed'
    jobsObj.end_time = timezone.now()
    jobsObj.save()

    if err != "":
        try:
            logger.info("error file save to error_file")
            logger.info(str(err))

            if wrong_csv_uploaded is False:
                jobsObj.error_file=errorfilename
            jobsObj.status = 'Completed With Errors'
            if jobsObj.error_details is None:
                jobsObj.error_details = "Download error file and re-upload it after corrections if any error found"
            jobsObj.save()
        except Exception as e:
            logger.info(str(e))
        return True
    else:
        try:
            os.remove(errorfilepath)
            logger.info("success return True")
        except Exception as e:
            logger.info(str(e))
        return True

@task()
def SugarUpdateTask():
    from api.models import Company,UserProfile,CatalogEnquiry
    from api.v1.sugar_crm import update_user_to_crm,update_company_to_crm,update_enquiry_to_crm
    from django.db.models import Q
    userprofiles = UserProfile.objects.exclude(Q(sugar_crm_user_id__isnull=True) | Q(sugar_crm_user_id__exact='')).order_by('user_id')
    for userprofile in userprofiles:
        logger.info("crm_update_crone userprofile.user_id = %s"% (userprofile.user_id))
        update_user_to_crm(userprofile.user_id,False)

    companies = Company.objects.exclude(Q(sugar_crm_account_id__isnull=True) | Q(sugar_crm_account_id__exact='')).order_by('id')
    for company in companies:
        logger.info("crm_update_crone company.id = %s"% (company.id))
        update_company_to_crm(company.id,False)

    enquiries = CatalogEnquiry.objects.exclude(Q(sugar_crm_lead_id__isnull=True) | Q(sugar_crm_lead_id__exact='')).order_by('id')
    for enquiry in enquiries:
        logger.info("crm_update_crone enquiry.id = %s"% (enquiry.id))
        update_enquiry_to_crm(enquiry.id,False)
    return True


@task()
def SugarCallUpdateTask():
	from django.contrib.auth.models import User
	from api.v1.sugar_crm import update_call_to_crm
	from django.db.models import Q

	todayDate       = datetime.now()
	yesterdayDate   = todayDate - timedelta(days=1)

	#for invitee call
	invite_call_users           = User.objects.filter(date_joined__gte=yesterdayDate, userprofile__first_login__isnull=True, last_login__isnull=True)
	for user in invite_call_users:
		logger.info("crm_call_update_crone user_id = %s"% (user.id))
		update_call_to_crm(user.id,"invite_call")

	#for welcome call
	welcome_call_users = User.objects.filter(userprofile__first_login__gte=yesterdayDate)
	for user in welcome_call_users:
		logger.info("crm_call_update_crone user_id = %s"% (user.id))
		update_call_to_crm(user.id,"welcome_call")
	return True

@task()
def UpdateUninstallUsersTask():
	from datetime import date, datetime, timedelta
	from django.db.models import Sum, Min, Max, Count
	from api.models import UserProfile
	from api.common_functions import getCompanyTypeArray,read_google_sheets_data, get_google_sheets_service, write_data_to_google_sheets
	import csv
	import StringIO
	from django.utils import timezone

	logger.info("in UpdateUninstallUsersTask Start")

	todayDate = date.today()
	lastDate = todayDate - timedelta(days=1)
	#lastDate = todayDate - timedelta(hours=6) #every 6 hours run cron
	logger.info("in UpdateUninstallUsersTask lastDate = %s"% (lastDate))

	#to get and set uninstall users start
	from push_notifications.models import GCMDevice ,APNSDevice

	alldevices = GCMDevice.objects.filter(active=True)
	status = alldevices.send_message(None)
	logger.info("in UpdateUninstallUsersTask GCMDevice alldevices send_message None status = %s"% (status))

	try:
		alldevices = APNSDevice.objects.filter(active=True)
		status = alldevices.send_message(None)
		logger.info("in UpdateUninstallUsersTask GCMDevice alldevices send_message None status = %s"% (status))
	except Exception as e:
		pass

	active_users_gcm = GCMDevice.objects.filter(active=True).values_list('user', flat=True)
	active_users_apns = APNSDevice.objects.filter(active=True).values_list('user', flat=True)
	UserProfile.objects.filter(Q(uninstall_date__isnull=False) & Q(Q(user__in=active_users_gcm) | Q(user__in=active_users_apns))).update(uninstall_date=None)

	uninstall_users = UserProfile.objects.filter(uninstall_date__isnull=False).values_list('user', flat=True)
	uninstall_users = list(uninstall_users)

	inactive_users_gcm = GCMDevice.objects.filter(active=False).exclude(Q(user__in=active_users_gcm) | Q(user__in=uninstall_users)).values_list('user', flat=True)
	inactive_users_apns = APNSDevice.objects.filter(active=False).exclude(Q(user__in=active_users_apns) | Q(user__in=uninstall_users)).values_list('user', flat=True)

	# print "uninstall_users = ",uninstall_users
	# print "inactive_users_gcm = ",inactive_users_gcm
	# print "inactive_users_apns = ",inactive_users_apns

	profileupdated = UserProfile.objects.filter(Q(user__in=inactive_users_gcm) | Q(user__in=inactive_users_apns)).update(uninstall_date=lastDate)
	logger.info("in UpdateUninstallUsersTask total profileupdated = %s"% (profileupdated))
	#to get and set uninstall users end

	import os

	#to write in google sheet start
	#from __future__ import print_function
	from googleapiclient.discovery import build
	from httplib2 import Http
	from oauth2client import file, client, tools
	#to write in google sheet end

	SPREADSHEET_ID = '1ftcCPXRusT-jjNrrkzTM4h6kYetv9XaDrul0KHoynI4' #for final csv file which is used by BD team
	RANGE_NAME = 'CallingSheet!A:H'
	send_email_to = ["tech@wishbook.io", "supportdesk@wishbook.io", "virender@wishbook.io", "deepikad@wishbook.io", "gaurav@wishbook.io"]

	if settings.DEBUG:
		logger.info("UpdateUninstallUsersTask if settings.DEBUG=True")
		SPREADSHEET_ID = '1XZYRyf-hBJictQyp-7EHeN_Dfz1FdtuJqS4NmJbyyrg' #for DailyWishbookUpdatedOrders gooogle sheet
		RANGE_NAME = 'Sheet1!A:H'
		send_email_to = ["tech@wishbook.io"]


	#to write in google sheet start
	# Setup the Sheets API


	# SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
	# configdir = os.path.expanduser('google_sheet/')
	# credentials = os.path.join(configdir, 'credentials.json')
	# store = file.Storage(credentials)
	# creds = store.get()
	# if not creds or creds.invalid:
	# 	client_secrets = os.path.join(configdir, 'client_secret.json')
	# 	flow = client.flow_from_clientsecrets(client_secrets, SCOPES)
	# 	creds = tools.run_flow(flow, store)
	# service = build('sheets', 'v4', http=creds.authorize(Http()))



	# exclude_order_ids = []
	# Call the Sheets API
	# result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
	# values = result.get('values', [])
	# if not values:
	# 	print 'No data found.'
	# else:
	# 	for row in values:
	# 		if row[0] != "" and row[0] is not None:
	# 			try:
	# 				if int(row[0]) not in exclude_order_ids:
	# 					exclude_order_ids.append(int(row[0]))
	# 			except Exception as e:
	# 				pass

	#logger.info("in DailyOrderCSVeMailTask exclude_order_ids = %s"% (exclude_order_ids))

	all_data_arr = []

	try:
		queryset = UserProfile.objects.filter(uninstall_date=lastDate)#.exclude(id__in=exclude_order_ids)
		print "queryset =",queryset

		# csvfile = StringIO.StringIO()
		# writer = csv.writer(csvfile)
		# writer.writerow(['order_id', 'invoice_id', 'order_date', 'payment_date', 'payment_detail', 'payment_status', 'is_full_catalog', 'brand_name', 'catalog_name', 'total_qty', 'amount', 'discount', 'taxes', 'shipping_amount', 'total_amount', 'payment_id', 'buyer_name', 'buyer_phone_number', 'buyer_gst_pan', 'buyer_city', 'buyer_state', 'buyer_full_address', 'seller_name', 'seller_phoen_number', 'seller_gst_pan', 'seller_city', 'seller_state', 'additional_details', 'ship_to'])

		for userprofile in queryset:
			try:
				logger.info("in UpdateUninstallUsersTask user.id = %s"% (userprofile.user_id))

				# uninstall_date = str(timezone.localtime(userprofile.uninstall_date).strftime("%d/%m/%Y : %I:%M%p"))
				install_date = ""
				try:
					install_date = str(userprofile.first_login.strftime("%d/%m/%Y"))
				except Exception as e:
					install_date = str(userprofile.user.date_joined.strftime("%d/%m/%Y"))

				uninstall_date = str(userprofile.uninstall_date.strftime("%d/%m/%Y"))
				company_name = comapny_types = ""
				try:
					company = userprofile.user.companyuser.company
					company_name = company.name
					comapny_types = getCompanyTypeArray(company.company_group_flag)
					comapny_types = ", ".join(comapny_types)
				except Exception as e:
					pass
				device_brand = device_name = device_os = ""
				try:
					userplatform = userprofile.user.userplatforminfo
					device_brand = userplatform.brand
					device_name = userplatform.device_model
					device_os = userplatform.operating_system
				except Exception as e:
					pass

				rowdata = [userprofile.user_id, userprofile.phone_number, company_name, comapny_types, install_date, uninstall_date, device_brand, device_name, device_os]

				# writer.writerow(rowdata)

				all_data_arr.append(rowdata)
			except Exception as e:
				logger.info("in UpdateUninstallUsersTask Exception for loop error = %s"% (e))
				import traceback
				logger.info("UpdateUninstallUsersTask Exception for loop traceback error = %s"% (traceback.format_exc()))
				pass


		# if len(all_data_arr) > 0:
		# 	print csvfile.getvalue()
		# 	mail = EmailMessage("Daily Orders CSV", "Please find the attached for Daily Orders", "tech@wishbook.io", send_email_to)
		# 	mail.attach("dailyorders.csv", csvfile.getvalue(), "text/csv")
		# 	mail.send()

		print "all_data_arr =", all_data_arr

		resource = {
		  "majorDimension": "ROWS",
		  "values": all_data_arr
		}

		# service.spreadsheets().values().append(
		#   spreadsheetId=SPREADSHEET_ID,
		#   range=RANGE_NAME,
		#   body=resource,
		#   valueInputOption="USER_ENTERED"
		# ).execute()
		VALUE_INPUT_OPTION = "USER_ENTERED"
		write_data_to_google_sheets(SPREADSHEET_ID, RANGE_NAME, resource, VALUE_INPUT_OPTION)
		#to write in google sheet end

	except Exception as e:
		logger.info("in UpdateUninstallUsersTask Exception error = %s"% (e))
		import traceback
		logger.info("UpdateUninstallUsersTask Exception traceback error = %s"% (traceback.format_exc()))
		pass

	logger.info("in UpdateUninstallUsersTask End")

@task()
def DailyOrderCSVeMailTask():
	#from __future__ import *
	#from api.common_functions import read_google_sheets_data, write_data_to_google_sheets
	from datetime import date, datetime, timedelta
	# from django.db.models import Sum, Min, Max, Count
	from api.models import SalesOrder, Invoice, Shipment#, Catalog, Invoice, Payment, CompanyKycTaxation
	from api.common_functions import read_google_sheets_data, write_data_to_google_sheets, update_individual_sheets_rows, compute_order_details
	import csv
	import StringIO
	from django.utils import timezone

	import os

	#to write in google sheet start
	#from __future__ import print_function
	# from googleapiclient.discovery import build
	# from httplib2 import Http
	# from oauth2client import file, client, tools
	#to write in google sheet end

	logger.info("in DailyOrderCSVeMailTask Start")

	SPREADSHEET_ID = '1-d32W_do0ZqJR-CuybAFxEo3c77nhJ8Sotx6KmSLb60' #for final csv file which is used by BD team
	RANGE_NAME = 'Main!A:AF' #till AG
	send_email_to = ["tech@wishbook.io", "supportdesk@wishbook.io", "virender@wishbook.io", "deepikad@wishbook.io", "gaurav@wishbook.io"]

	if settings.DEBUG:
		logger.info("DailyOrderCSVeMailTask if settings.DEBUG=True")
		SPREADSHEET_ID = '1E-yoaqHJf5X86aifo4PafX0BYpUyxaLgoeDxUn0znUs' #for DailyWishbookUpdatedOrders gooogle sheet
		RANGE_NAME = 'Sheet4!A:AF' #'Sheet1!A:AF'
		send_email_to = ["tech@wishbook.io"]


	#to write in google sheet start
	# Setup the Sheets API
	# SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
	# configdir = os.path.expanduser('google_sheet/')
	# credentials = os.path.join(configdir, 'credentials.json')
	# store = file.Storage(credentials)
	# creds = store.get()
	# if not creds or creds.invalid:
	# 	client_secrets = os.path.join(configdir, 'client_secret.json')
	# 	flow = client.flow_from_clientsecrets(client_secrets, SCOPES)
	# 	creds = tools.run_flow(flow, store)
	# service = build('sheets', 'v4', http=creds.authorize(Http()))

	exclude_order_ids = []
	row_numbers = {}

	# Call the Sheets API
	#result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
	result = read_google_sheets_data(SPREADSHEET_ID, RANGE_NAME)
	values = result.get('values', [])
	if not values:
		print 'No data found.'
	else:
		for i, row in enumerate(values):
			#logger.info("ROW: %s" % row)
			# Print columns A and E, which correspond to indices 0 and 4.
			#print row[0], row[3]
			if row[0] != "" and row[0] is not None and row[0]!='order_id' and row[0] != []:
				try:
					if int(row[0]) not in exclude_order_ids:
						exclude_order_ids.append(int(row[0]))
						row_numbers[int(row[0])]=i #saving the row number from sheet
				except Exception as e:
					pass

	#logger.info("in DailyOrderCSVeMailTask exclude_order_ids = %s"% (exclude_order_ids))

	all_data_arr = []

	try:
		todayDate = datetime.now()
		lastDate = todayDate - timedelta(days=1)
		#lastDate = todayDate - timedelta(hours=6) #every 6 hours run cron
		logger.info("in DailyOrderCSVeMailTask lastDate = %s"% (lastDate))

		# credit_queryset = SalesOrder.objects.filter(order_type="Credit", payment_date__gte=lastDate).exclude(id__in=exclude_order_ids)
		ecompany_ids = [174, 241000]
		credit_queryset = SalesOrder.objects.filter(order_type="Credit", source_type="Marketplace", created_at__gte=lastDate).values_list('id', flat=True)#.exclude(Q(id__in=exclude_order_ids) | Q(company__in=ecompany_ids) | Q(seller_company__in=ecompany_ids)) #should show all credit order. sug. by gaurav
		paid_queryset = SalesOrder.objects.filter(payment_date__gte=lastDate).exclude(order_type="Credit").values_list('id', flat=True)#.exclude(Q(id__in=exclude_order_ids) | Q(company__in=ecompany_ids) | Q(seller_company__in=ecompany_ids))
		#paid_queryset = filterOrderPaymentStatus(paid_queryset, "Paid or Partially Paid")

		# logger.info("in DailyOrderCSVeMailTask credit_queryset = %s"% (credit_queryset))
		# logger.info("in DailyOrderCSVeMailTask paid_queryset = %s"% (paid_queryset))

		queryset = SalesOrder.objects.filter(Q(id__in=credit_queryset) | Q(id__in=paid_queryset)).exclude(Q(id__in=exclude_order_ids) | Q(company__in=ecompany_ids) | Q(seller_company__in=ecompany_ids)).select_related('company', 'seller_company').prefetch_related('items', 'company__address__city', 'seller_company__address__city')

		orders_shipment_updated = SalesOrder.objects.filter(id__in=Invoice.objects.filter(id__in=Shipment.objects.filter(modified__gte=lastDate).values_list('invoice', flat =True)).values_list('order', flat =True)).values_list('id', flat=True)
		# queryset_for_updating = SalesOrder.objects.filter(Q(Q(id__in=exclude_order_ids) & Q(time__gte=lastDate)) | Q(id__in=orders_shipment_updated)).exclude(created_at__gte=lastDate)
		queryset_for_updating = SalesOrder.objects.filter(Q(id__in=exclude_order_ids) & Q(Q(time__gte=lastDate) | Q(id__in=orders_shipment_updated))).exclude(Q(id__in=credit_queryset) | Q(id__in=paid_queryset))#.exclude(created_at__gte=lastDate)

		csvfile = StringIO.StringIO()
		writer = csv.writer(csvfile)
		writer.writerow(['order_id', 'invoice_id', 'order_date', 'payment_date', 'payment_detail', 'payment_status', 'is_full_catalog', 'brand_name', 'catalog_name', 'total_qty', 'amount', 'discount', 'taxes', 'shipping_amount', 'total_amount', 'payment_id', 'buyer_name', 'buyer_phone_number', 'buyer_gst_pan', 'buyer_city', 'buyer_state', 'buyer_full_address', 'seller_name', 'seller_phoen_number', 'seller_gst_pan', 'seller_city', 'seller_state', 'additional_details', 'ship_to', 'buyer_account_details', 'seller_account_details','traking_numbers_and_courier_names'])

		all_data_arr = compute_order_details(queryset)

		update_orders_arr = compute_order_details(queryset_for_updating)

		# for salesorder in queryset:
		# 	payment_details = salesorder.payment_details
		# 	if payment_details is not None and "Mode : Zaakpay" in payment_details and "Status : Pending" in payment_details:
		# 		continue
        #
		# 	try:
		# 		logger.info("in DailyOrderCSVeMailTask salesorder.id = %s"% (salesorder.id))
		# 		catalogs = salesorder.items.all().values_list('product__catalog', flat=True).distinct()
		# 		catalogs = Catalog.objects.filter(id__in=catalogs)
        #
		# 		buyer_gst_pan = ""
		# 		if CompanyKycTaxation.objects.filter(company=salesorder.company).exists():
		# 			kyc = salesorder.company.kyc
		# 			if kyc.gstin:
		# 				buyer_gst_pan += "GST - " + kyc.gstin + "\n"
		# 			if kyc.pan:
		# 				buyer_gst_pan += "Pan - " + kyc.pan
        #
		# 		seller_gst_pan = ""
		# 		if CompanyKycTaxation.objects.filter(company=salesorder.seller_company).exists():
		# 			kyc = salesorder.seller_company.kyc
		# 			if kyc.gstin:
		# 				seller_gst_pan += "GST - " + kyc.gstin + "\n"
		# 			if kyc.pan:
		# 				seller_gst_pan += "Pan - " + kyc.pan
        #
		# 		ship_to = ""
		# 		if salesorder.ship_to:
		# 			if salesorder.ship_to.street_address:
		# 				ship_to = salesorder.ship_to.street_address
		# 			if salesorder.ship_to.state:
		# 				ship_to += ", "+salesorder.ship_to.state.state_name
		# 			if salesorder.ship_to.city:
		# 				ship_to += ", "+salesorder.ship_to.city.city_name
        #
		# 		invoices = Invoice.objects.filter(order=salesorder)
		# 		invoice_ids = invoices.values_list('id', flat=True)
        #
		# 		payment_ids = Payment.objects.filter(invoice__in=invoice_ids).values_list('id', flat=True)
        #
		# 		invoice_ids = map(str, invoice_ids)
		# 		invoice_ids = ", ".join(invoice_ids)
        #
		# 		payment_ids = map(str, payment_ids)
		# 		payment_ids = ", ".join(payment_ids)
        #
		# 		for catalog in catalogs:
		# 			shipping_charges = 0
		# 			amount = 0
		# 			total_amount = 0
		# 			discount = 0
		# 			taxes = 0
		# 			qty = 0
		# 			for invoice in invoices:
		# 				shipping_charges += invoice.shipping_charges
        #
		# 				items = invoice.items.filter(order_item__product__catalog=catalog)
		# 				for item in items:
		# 					amount += item.amount
		# 					total_amount += item.total_amount
		# 					discount += item.discount
		# 					taxes += item.tax_value_1 + item.tax_value_2
		# 					qty += item.qty
        #
		# 			created_at = str(timezone.localtime(salesorder.created_at).strftime("%d/%m/%Y"))
		# 			payment_date = ""
		# 			if salesorder.payment_date:
		# 				payment_date = str(salesorder.payment_date.strftime("%d/%m/%Y"))
		# 			rowdata = [salesorder.pk, invoice_ids, created_at, payment_date, salesorder.payment_details, salesorder.payment_status(), catalog.sell_full_catalog, catalog.brand.name, catalog.title, qty, str(amount), str(discount), str(taxes), str(shipping_charges), str(total_amount), payment_ids, salesorder.company.name, salesorder.company.phone_number, buyer_gst_pan, salesorder.company.address.city.city_name, salesorder.company.address.state.state_name, salesorder.company.address.street_address, salesorder.seller_company.name, salesorder.seller_company.phone_number, seller_gst_pan, salesorder.seller_company.address.city.city_name, salesorder.seller_company.address.state.state_name, salesorder.note, ship_to]
        #
		# 			all_data_arr.append(rowdata)
		# 			writer.writerow(rowdata)
        #
        #
		# 	except Exception as e:
		# 		logger.info("in DailyOrderCSVeMailTask Exception for loop error = %s"% (e))
		# 		import traceback
		# 		logger.info("DailyOrderCSVeMailTask Exception for loop traceback error = %s"% (traceback.format_exc()))
		# 		pass

		all_resource = {
		  "majorDimension": "ROWS",
		  "values": all_data_arr
		}

		updating_resource = {
		"values": update_orders_arr
		}

		VALUE_INPUT_OPTION = "USER_ENTERED"


		update_individual_sheets_rows(SPREADSHEET_ID, RANGE_NAME, updating_resource, VALUE_INPUT_OPTION, row_numbers)

		write_data_to_google_sheets(SPREADSHEET_ID, RANGE_NAME, all_resource, VALUE_INPUT_OPTION)

		if len(all_data_arr) > 0:
			for rowdata in all_data_arr:
				writer.writerow(rowdata)

			print csvfile.getvalue()
			mail = EmailMessage("Daily Orders CSV", "Please find the attached for Daily Orders", "tech@wishbook.io", send_email_to)
			# mail = EmailMessage("Daily Orders CSV", "Please find the attached for Daily Orders", "tech@wishbook.io", ["tech@wishbook.io"])
			mail.attach("dailyorders.csv", csvfile.getvalue(), "text/csv")
			mail.send()

		# resource = {
		#   "majorDimension": "ROWS",
		#   "values": all_data_arr
		# }

		# service.spreadsheets().values().append(
		#   spreadsheetId=SPREADSHEET_ID,
		#   range=RANGE_NAME,
		#   body=resource,
		#   valueInputOption="USER_ENTERED"
		# ).execute()

		# VALUE_INPUT_OPTION = "USER_ENTERED"
		# write_data_to_google_sheets(SPREADSHEET_ID, RANGE_NAME, resource, VALUE_INPUT_OPTION)
		#to write in google sheet end

	except Exception as e:
		logger.info("in DailyOrderCSVeMailTask Exception error = %s"% (e))
		import traceback
		logger.info("DailyOrderCSVeMailTask Exception traceback error = %s"% (traceback.format_exc()))
		pass

	logger.info("in DailyOrderCSVeMailTask End")

def handle_csv_error(field_name,writer,row,err=''):

    if err:
        row["error"] = err
        logger.info("field error %s" % err )
        writer.writerow(row)
        return
    err = str(field_name) + " is not Found"
    row["error"] = err
    logger.info("field error %s" % err )
    writer.writerow(row)
    return



#WB-2198 - create new function in task.py file for cron
@task()
def dailyUnsubscribedNumberCSVreaderTask():
	#from __future__ import *
	logger.info("in dailyUnsubscribedNumberCSVreaderTask Start")

	from api.models import Country, UnsubscribedNumber, UserContact, UserProfile
	from api.common_functions import smsUrl,read_google_sheets_data, get_google_sheets_service, write_data_to_google_sheets

	SPREADSHEET_ID = '1rtszWjns4AZ2F2fzH73f9DQitQ3blzOlaFk-qKMYwgA' #for final csv file which is used by BD team
	RANGE_NAME = 'For Tech!A:A'
	send_email_to = ["tech@wishbook.io", "supportdesk@wishbook.io", "virender@wishbook.io", "deepikad@wishbook.io", "gaurav@wishbook.io"]

	if settings.DEBUG:
		logger.info("dailyUnsubscribedNumberCSVreaderTask if settings.DEBUG=True")
		SPREADSHEET_ID = '1rtszWjns4AZ2F2fzH73f9DQitQ3blzOlaFk-qKMYwgA' #for DailyWishbookUpdatedOrders gooogle sheet
		RANGE_NAME = 'For Tech!A:A'
		send_email_to = ["tech@wishbook.io"]


	result = read_google_sheets_data(SPREADSHEET_ID, RANGE_NAME)

	if not result:
		logger.info("No results")
		return
	ph_numbers = []
	for row in result['values'][1:]:
		if row != "" and row is not None and row not in ph_numbers:
			ph_numbers.append(''.join(row).strip())

	country = Country.objects.filter(name__icontains='India').first()
	for num in ph_numbers:
		if len(num) != 10:
			continue
		else:
			user_profile = UserProfile.objects.filter(phone_number=num).select_related('user').first()
			if user_profile is None:
				continue
			else:
				unsub_obj, created = UnsubscribedNumber.objects.get_or_create(phone_number=num, country=country)
				user_obj = user_profile.user
				if user_obj and user_obj.is_active:
					user_obj.is_active = False
					user_obj.save()
					#logger.info('dailyUnsubscribedNumberCSVreaderTask: number: %s user %s is inactive' % (num, user_obj))
				else:
					logger.info('dailyUnsubscribedNumberCSVreaderTask: number: %s user %s already inactive or doesnot exists' % (num, user_obj))

def strip_csv(strip_list):
    return [x.strip() for x in strip_list ]
