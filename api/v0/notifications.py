from notifier.shortcuts import create_notification

#create_notification('email-notification')
#create_notification('sms-notification', display_name='SMSNotification' , backends='sms-notification')
#create_notification('mobile-notification', display_name='MobileNotification' , backends='mobile-notification')
#create_notification('chat', display_name='Chat' , backends='chat')

create_notification('otp')
create_notification('sales-order')
create_notification('purchase-order')
create_notification('buyer-request')
create_notification('supplier-request')
create_notification('share-received')
create_notification('order-status')
create_notification('share')
