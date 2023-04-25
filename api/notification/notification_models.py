from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class BaseModel(models.Model):
    """
    Base class for common fields
    """
    created  = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class Notification(BaseModel):
    """
        class for storing notification data.
        manual refers to trigger by admin.
    """

    MSG_WAY = (
        ('Manual','Manual'),
        ('Automate','Automate'),
    )

    msg_way         = models.CharField(max_length=100,choices=MSG_WAY,default='Manual')
    created_by      = models.ForeignKey('auth.User',on_delete=models.CASCADE, related_name='trigger_notifications')
    notice_template = models.ForeignKey('NotificationEntityTemplate',verbose_name ="notice template",on_delete=models.SET_NULL,related_name='notifications',null=True)
    message         = models.TextField(blank=True)
    notifier_users  = models.TextField(blank=True,default=None)
    extra_ids       = models.CharField(max_length=250,blank=True,default=None)
    content_type    = models.ForeignKey(ContentType,null=True,blank=True,on_delete=models.SET_NULL)
    object_id       = models.PositiveIntegerField(null=True, blank=True)
    content_object  = GenericForeignKey("content_type", "object_id")
    is_sent         = models.BooleanField(default=False)

    class Meta:
        app_label           = 'api'
        verbose_name        = "notification"
        verbose_name_plural = "notifications"

    def __unicode__(self):
        return "%s : %s" %(self.created_by,self.notice_template.label)


class NotificationEntity(BaseModel):
    """
        Notification Entity refers to which model notification is targeted.
    """
    entity_name = models.CharField(max_length=100,unique=True)

    class Meta:
       app_label            = 'api'
       verbose_name         = "notification entity"
       verbose_name_plural  = "notification entities"

    def __unicode__(self):
        return self.entity_name


class NotificationEntityTemplate(BaseModel):
    """
        Template for notifaction
    """

    TEMPLATE_LANGUAGE = (
        ('Hindi','Hindi'),
        ('English','English'),
    )

    entity              = models.ForeignKey('NotificationEntity',verbose_name ="notification entity",on_delete=models.CASCADE)
    label               = models.CharField(max_length=250)
    description         = models.TextField(blank=True, null=True)
    language            = models.CharField(choices=TEMPLATE_LANGUAGE,max_length=20,default='English')
    is_sms              = models.BooleanField(default=False)
    sms_temp            = models.TextField(blank=True,default=None)
    is_notification     = models.BooleanField(default=False)
    notification_temp   = models.TextField(blank=True,default=None)
    is_email            = models.BooleanField(default=False)
    email_temp          = models.TextField(blank=True,default=None)
    is_inapp            = models.BooleanField(default=False)
    inapp_temp          = models.TextField(blank=True,default=None)
    receiver            = models.CharField(blank=True,default=None,max_length=250)

    class Meta:
        app_label           = 'api'
        verbose_name        = "notification entity Template"
        verbose_name_plural = "notification entity Templates"
        unique_together     = ('entity','label',)

    def __unicode__(self):
        return ("{} : {}" .format(self.entity.entity_name,self.label)) 
