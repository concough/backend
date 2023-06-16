from __future__ import division
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models
from django.contrib.auth.models import Permission, AbstractUser, User
from django.contrib.contenttypes.models import ContentType
from django.utils.datetime_safe import datetime

from digikunkor.settings import USER_WALLET
from main.Helpers.model_static_values import ENTRANCE_TAG_SALE_Q_COUNT
from main.models_helper import NoDeleteFileStorage
from models_helper import ContentTypeRestrictedImageField
from PIL import Image
from cStringIO import StringIO


# Create your models here.
# 2018-04-23
class Tags(models.Model):
    title = models.CharField(max_length=250, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s" % (self.title, )


# Concough Log Tables
class ConcoughActivity(models.Model):
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name="activity_obj")
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    activity_type = models.CharField(max_length=100)

    class Meta:
        ordering = ('-created',)


class ConcoughUserPurchased(models.Model):
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name="pruchase_obj")
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')

    user = models.ForeignKey(User, related_name="purchased")
    payed_amount = models.IntegerField(null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    downloaded = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created',)
        unique_together = ('user', 'target_ct', 'target_id')


class ConcoughProductStatistic(models.Model):
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name="product_stat_obj")
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    downloaded = models.IntegerField(default=0)
    purchased = models.IntegerField(default=0)

    class Meta:
        unique_together = ('target_ct', 'target_id')


class ConcoughUserBasket(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name="basket", unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s: %s" % (self.user, self.unique_id)


class ConcoughUserSale(models.Model):
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name="sale_obj")
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')

    pay_amount = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    basket = models.ForeignKey(ConcoughUserBasket, related_name="sales")

    def __unicode__(self):
        return u"%s: %d" % (self.basket_id, self.pay_amount)

    class Meta:
        unique_together = ('basket', 'target_ct', 'target_id')


def get_org_image_path(instance, filename):
    if instance.image:
        django_type = instance.image.file.content_type
        if django_type == 'image/png':
            image_ext = 'png'
        filename = "Org/%s.%s" % (uuid.uuid4().get_hex(), image_ext)
    return filename


class Organization(models.Model):
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(max_length=100, upload_to=get_org_image_path, null=True)

    def __unicode__(self):
        return self.title


class EntranceType(models.Model):
    title = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, null=False)

    def __unicode__(self):
        return self.title


class ExaminationGroup(models.Model):
    title = models.CharField(max_length=200)
    etype = models.ForeignKey(EntranceType, related_name="groups")

    def __unicode__(self):
        return u"%s ~~ %s" % (self.etype, self.title)

    class Meta:
        unique_together = ('title', 'etype')


def get_set_image_path(instance, filename):
    if instance.image:
        django_type = instance.image.file.content_type
        if django_type == 'image/png':
            image_ext = 'png'
        filename = "Esets/%s.%s" % (uuid.uuid4().get_hex(), image_ext)
    return filename


class EntranceSet(models.Model):
    title = models.CharField(max_length=255)
    group = models.ForeignKey(ExaminationGroup, related_name="sets")
    image = models.ImageField(max_length=100, upload_to=get_set_image_path, null=True)
    code = models.IntegerField(null=False, default=0)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('title', 'group')

    def save(self, *args, **kwargs):
        if self.image:
            django_type = self.image.file.content_type

        try:
            this = EntranceSet.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)

        except:
            pass

        super(EntranceSet, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            storage, path = self.image.storage, self.image.path
            storage.delete(path)
        super(EntranceSet, self).delete(*args, **kwargs)

    def __unicode__(self):
        return u"%s (%s)" % (self.title, self.group)


class EntranceLesson(models.Model):
    title = models.CharField(max_length=200)
    full_title = models.CharField(max_length=500)
    entrance_type = models.ForeignKey(EntranceType, related_name="lessons")

    def __unicode__(self):
        return self.full_title


class Entrance(models.Model):
    organization = models.ForeignKey(Organization, related_name="entrances")
    entrance_type = models.ForeignKey(EntranceType, related_name="entrances")
    entrance_set = models.ForeignKey(EntranceSet, related_name="entrances")
    year = models.IntegerField()
    month = models.IntegerField()
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    published = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)
    last_published = models.DateTimeField(null=True)
    assigned_to_task = models.BooleanField(default=False)
    extra_data = models.CharField(default="", max_length=300)
    activity = GenericRelation(ConcoughActivity, related_query_name="entrance",
                               content_type_field='target_ct_id',
                               object_id_field='target_id',
                               )
    purchase = GenericRelation(ConcoughUserPurchased, related_query_name="entrance",
                               content_type_field='target_ct_id',
                               object_id_field='target_id',
                               )
    stats = GenericRelation(ConcoughProductStatistic, related_query_name="entrance",
                            content_type_field='target_ct_id',
                            object_id_field='target_id',
                            )
    sale = GenericRelation(ConcoughUserSale, related_query_name="entrance",
                           content_type_field='target_ct_id',
                           object_id_field='target_id',
                           )
    is_editing = models.BooleanField(default=True)

    class Meta:
        unique_together = ('organization', 'entrance_type', 'entrance_set', 'year', 'month')

    def __unicode__(self):
        return u"%s-%s: %s (%s/%s)" % (
        self.organization, self.entrance_type, self.entrance_set, str(self.year), str(self.month))


class EntranceSaleData(models.Model):
    entrance_type = models.ForeignKey(EntranceType, related_name="sale_data")
    cost = models.IntegerField(blank=False)
    cost_bon = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    year = models.IntegerField()
    month = models.IntegerField()

    def __unicode__(self):
        return u"%s (%4d/%2d) - %d" % (self.entrance_type, self.year, self.month, self.cost,)


class EntranceBooklet(models.Model):
    title = models.CharField(max_length=255)
    duration = models.PositiveSmallIntegerField(default=0)
    entrance = models.ForeignKey(Entrance, related_name="booklets")
    order = models.PositiveSmallIntegerField(default=1)
    optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ('title', 'entrance')

    def __unicode__(self):
        return u"%d) %s (%s)" % (self.order, self.title, self.entrance)


class EntranceBookletDetail(models.Model):
    booklet = models.ForeignKey(EntranceBooklet, related_name="bookletdetails")
    lesson = models.ForeignKey(EntranceLesson, related_name="bookletdetails")
    q_from = models.PositiveSmallIntegerField()
    q_to = models.PositiveSmallIntegerField()
    q_count = models.PositiveSmallIntegerField()
    order = models.PositiveSmallIntegerField(default=1)
    duration = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('booklet', 'lesson')

    def __unicode__(self):
        return u"%s: %d) %s(%d)" % (self.booklet, self.order, self.lesson, self.q_count)


def get_Q_image_path(instance, filename):
    if instance.image:
        django_type = instance.image.file.content_type
        if django_type == 'image/png':
            image_ext = 'png'

            entrance_unique_key = instance.question.booklet_detail.booklet.entrance.unique_key
            filename = "Qs/%s/%s.%s" % (entrance_unique_key.get_hex(),
                                        instance.unique_key.get_hex(), image_ext)

    return filename


class EntranceQuestion(models.Model):
    answer_key = models.PositiveSmallIntegerField()
    question_number = models.PositiveSmallIntegerField()
    booklet_detail = models.ForeignKey(EntranceBookletDetail, related_name="questions")
    tags = models.ManyToManyField(Tags, related_name="questions", default=None)

    class Meta:
        unique_together = ('booklet_detail', 'question_number')

    def __unicode__(self):
        return u"%d) %d" % (self.question_number, self.answer_key)

    def delete(self, *args, **kwargs):
        self.qs_images.delete()
        super(EntranceQuestion, self).delete(*args, **kwargs)


class EntranceQuestionImages(models.Model):
    image = ContentTypeRestrictedImageField(max_length=200, storage=NoDeleteFileStorage(), upload_to=get_Q_image_path,
                                            content_types=['image/png'],
                                            max_upload_size=1048576)
    question = models.ForeignKey(EntranceQuestion, related_name='qs_images')
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ('question', 'order')

    def save(self, *args, **kwargs):
        try:
            this = EntranceQuestionImages.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass

        super(EntranceQuestionImages, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(EntranceQuestionImages, self).delete(*args, **kwargs)


class EntranceSubset(models.Model):
    title = models.CharField(max_length=255)
    e_set = models.ForeignKey(EntranceSet, related_name="subsets")

    class Meta:
        unique_together = ('title', 'e_set')

    def __unicode__(self):
        return u"%s: %s" % (self.e_set, self.title)


class EntranceSubsetFactor(models.Model):
    subset = models.ForeignKey(EntranceSubset, related_name="factors")
    lesson = models.ForeignKey(EntranceLesson, related_name="factors")
    entrance = models.ForeignKey(Entrance, related_name="factors")
    factor = models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together = ('subset', 'lesson', 'entrance')

    def __unicode__(self):
        return u"%s: %s = %d" % (self.subset, self.lesson, self.factor)


class GlobalPermissionManager(models.Manager):
    def get_query_set(self):
        return super(GlobalPermissionManager, self). \
            get_query_set().filter(content_type__name='global_permission')


class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True
        verbose_name = "global_permission"

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            model=self._meta.verbose_name, app_label=self._meta.app_label,
        )
        self.content_type = ct
        super(GlobalPermission, self).save(*args)


class EntrancePackageType(models.Model):
    title = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class EntrancePackage(models.Model):
    entrance = models.ForeignKey(Entrance, related_name="packages")
    package_type = models.ForeignKey(EntrancePackageType, related_name="packages")
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(default=datetime.now)
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    content = models.TextField()
    minified = models.TextField()

    def __unicode__(self):
        return "package: {} for {}".format(self.package_type, self.entrance)


class EntranceLogType(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.title


class EntranceLog(models.Model):
    log_type = models.ForeignKey(EntranceLogType, related_name="logs")
    log_time = models.DateTimeField(auto_now_add=True)
    entrance = models.ForeignKey(Entrance, related_name="logs", default=1)
    data = models.TextField()

    def __unicode__(self):
        return "%s: (%s)" % (str(self.log_time), self.log_type)


class SmsStatus(models.Model):
    username = models.CharField(max_length=100)
    panel_name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    send_type = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s: %s - %s" % (self.username, self.status, self.panel_name)


class SmsCallStatus(models.Model):
    username = models.CharField(max_length=100)
    panel_name = models.CharField(max_length=100)
    status = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    send_type = models.CharField(max_length=100)
    sender = models.CharField(max_length=100)
    message_id = models.IntegerField()
    statustext = models.TextField()
    cost = models.IntegerField(default=0)
    sender_type = models.CharField(max_length=10, default="sms")

    def __unicode__(self):
        return "%s: %s - %s" % (self.username, self.status, self.panel_name)


def get_payment_provider_image_path(instance, filename):
    if instance.logo:
        django_type = instance.logo.file.content_type
        if django_type == 'image/png':
            image_ext = 'png'
        filename = "PaymentProvider/%s.%s" % (uuid.uuid4().get_hex(), image_ext)
    return filename


class PaymentProvider(models.Model):
    name = models.CharField(max_length=100)
    mmerchant_id = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    callback_url = models.TextField()
    webservice_url = models.TextField()
    pay_url = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(max_length=100, upload_to=get_payment_provider_image_path, null=True)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.webservice_url)


class ConcoughPayments(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='payments')
    basket = models.ForeignKey(ConcoughUserBasket, null=True, related_name='payments', on_delete=models.SET_NULL)
    amount = models.IntegerField()
    description = models.TextField(null=True)
    authority = models.TextField(null=True)
    state = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    provider = models.ForeignKey(PaymentProvider, related_name='payments')
    provider_status = models.CharField(max_length=200, null=True)
    ref_id = models.CharField(max_length=300, null=True)

    def __unicode__(self):
        return "%s(%s): %d - %s/%s" % (self.user, self.basket, self.amount, self.state, self.provider_status)


# Added at 4/12/17
class UserFinanialInformation(models.Model):
    user = models.OneToOneField(User, related_name='finance_info')
    bank_name = models.CharField(max_length=100)
    bank_account_no = models.CharField(max_length=30, null=True)
    bank_shaba = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s: %s" % (self.user, self.bank_shaba)


class EntranceEditorFinanialPayment(models.Model):
    user = models.ForeignKey(User, related_name='edit_payments')
    created = models.DateTimeField(auto_now_add=True)
    job_type = models.CharField(max_length=100)
    payed = models.IntegerField(default=0)
    job_id = models.UUIDField()
    deposit_id = models.CharField(max_length=100)
    issue_tracking = models.CharField(max_length=100, null=True)
    seen = models.BooleanField(default=False)
    description = models.CharField(max_length=500, default="")

    def __unicode__(self):
        return "%s > %s: %s" % (self.created, self.user, self.payed)


class EntranceCheckerFinanialPayment(models.Model):
    user = models.ForeignKey(User, related_name='entrance_check_payments')
    created = models.DateTimeField(auto_now_add=True)
    job_type = models.CharField(max_length=100)
    payed = models.IntegerField(default=0)
    deposit_id = models.CharField(max_length=100)
    issue_tracking = models.CharField(max_length=100, null=True)
    seen = models.BooleanField(default=False)
    description = models.CharField(max_length=1000, default="")

    def __unicode__(self):
        return "%s > %s: %s" % (self.created, self.user, self.payed)


class UserCheckerState(models.Model):
    user = models.OneToOneField(User, related_name='checker_state', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=10)


class UserCheckerEntranceCost(models.Model):
    title = models.CharField(max_length=255)
    updated = models.DateTimeField(auto_now=True)
    cost = models.IntegerField(default=0)
    rate = models.FloatField(default=1.0)

    def __unicode__(self):
        return "%s > %s: %s" % (self.title, self.cost, self.rate)


class StaffUserRate(models.Model):
    user = models.OneToOneField(User, related_name='rate', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    rate = models.FloatField(default=0.0)
    rate_count = models.BigIntegerField(default=0)

    def __unicode__(self):
        return "%s > %s" % (self.user, self.rate)


class ContentQuotesCategory(models.Model):
    title = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "%s > %s" % (self.code, self.title)


def get_content_quote_image_path(instance, filename):
    if instance.main_image:
        django_type = instance.main_image.file.content_type
        if django_type == 'image/png':
            image_ext = 'png'
            filename = "Content/Quotes/%s.%s" % (instance.unique_key.get_hex(), image_ext)
        elif django_type == 'image/jpeg':
            image_ext = 'jpg'
            filename = "Content/Quotes/%s.%s" % (instance.unique_key.get_hex(), image_ext)

    return filename


def get_content_quote_back_image_path(instance, filename):
    if instance.main_image_back:
        django_type = instance.main_image_back.file.content_type
        if django_type == 'image/png':
            image_ext = 'png'
            filename = "Content/Quotes/%s_back.%s" % (instance.unique_key.get_hex(), image_ext)
        elif django_type == 'image/jpeg':
            image_ext = 'jpg'
            filename = "Content/Quotes/%s_back.%s" % (instance.unique_key.get_hex(), image_ext)

    return filename


class ContentQuote(models.Model):
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, related_name="quotes")
    title_fa = models.TextField()
    title_en = models.TextField()
    company_name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    app_show_count = models.IntegerField(default=0)
    blog_show_count = models.IntegerField(default=0)
    title_back_color = models.CharField(max_length=10)
    title_back_alpha = models.FloatField(default=0.0)
    author = models.CharField(max_length=100)
    category = models.ManyToManyField(ContentQuotesCategory, related_name="quotes")
    main_image = ContentTypeRestrictedImageField(max_length=200, upload_to=get_content_quote_image_path,
                                                 content_types=['image/png', 'image/jpeg'],
                                                 max_upload_size=1048576)
    main_image_back = ContentTypeRestrictedImageField(max_length=200,
                                                      upload_to=get_content_quote_back_image_path,
                                                      content_types=['image/png', 'image/jpeg'],
                                                      max_upload_size=1048576)
    activity = GenericRelation(ConcoughActivity, related_query_name="ContentQuote",
                               content_type_field='target_ct_id',
                               object_id_field='target_id',
                               )

    def __unicode__(self):
        return "%s > %d-%d (%s)" % (self.title_fa, self.app_show_count, self.blog_show_count, self.category)

    def save(self, *args, **kwargs):
        try:
            this = ContentQuote.objects.get(id=self.id)
            if this.main_image != self.main_image:
                this.main_image.delete(save=False)
                this.main_image_back.delete(save=False)

        except:
            pass

        super(ContentQuote, self).save(*args, **kwargs)
        self.make_thumbnails()

    def delete(self, *args, **kwargs):
        if self.main_image:
            storage, path = self.main_image.storage, self.main_image.path
            storage.delete(path)
            storage.delete("%s_1280.%s"% (path.split('.')[0], path.split('.')[1]))
            storage, path = self.main_image_back.storage, self.main_image_back.path
            storage.delete(path)
            storage.delete("%s_1280.%s" % (path.split('.')[0], path.split('.')[1]))
        super(ContentQuote, self).delete(*args, **kwargs)

    def make_thumbnails(self):
        if not self.main_image:
            return

        FILE_EXTENSION = self.main_image.path.split('.')[-1]

        width = 1280

        image = Image.open(StringIO(self.main_image.read()))
        pic_width = image.size[0]

        ratio = width / float(pic_width)
        THUMBNAIL_SIZE1 = (width, int(image.size[1] * ratio))

        base_path1 = self.main_image.path.rsplit('/', 1)[0]

        image = image.resize(THUMBNAIL_SIZE1)
        image.save("%s/%s_1280.%s" % (base_path1, self.unique_key.get_hex(), FILE_EXTENSION))

        # 2
        image = Image.open(StringIO(self.main_image_back.read()))
        pic_width = image.size[0]

        ratio = width / float(pic_width)
        THUMBNAIL_SIZE2 = (width, int(image.size[1] * ratio))

        base_path2 = self.main_image_back.path.rsplit('/', 1)[0]

        image = image.resize(THUMBNAIL_SIZE2)
        image.save("%s/%s_back_1280.%s" % (base_path2, self.unique_key.get_hex(), FILE_EXTENSION))


# Concough Gift Cards
class ConcoughGiftCard(models.Model):
    cost = models.IntegerField(blank=False, default=0)
    description = models.CharField(max_length=300, null=False)
    gift_type = models.CharField(choices=CONCOUGH_GIFT_CARD_TYPES, max_length=25)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    charge = models.IntegerField(default=0)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)

    def __unicode__(self):
        return u"%s:%d = %d - %s" % (self.gift_type, self.cost, self.charge, self.description)


# Wallet Models
class UserWallet(models.Model):
    user = models.OneToOneField(User, related_name='wallet', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    cash = models.IntegerField(default=USER_WALLET)

    def __unicode__(self):
        return "%s > %s" % (self.user, self.cash)


class UserWalletTransaction(models.Model):
    wallet = models.ForeignKey(UserWallet, related_name="transactions")
    cost = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True)
    operation = models.CharField(max_length=100, null=False)
    gift_card = models.ForeignKey(ConcoughGiftCard, related_name="wallet_transactions", null=True)

    def __unicode__(self):
        return "%s: %s - %s" % (self.wallet, self.operation, self.description)


# Entrance Multi
class EntranceMulti(models.Model):
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    published = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    entrances = models.ManyToManyField(Entrance, related_name="entrancemulti")
    activity = GenericRelation(ConcoughActivity, related_query_name="entrancemulti",
                               content_type_field='target_ct_id',
                               object_id_field='target_id',
                               )


class EntranceLessonTagPackage(models.Model):
    booklet_detail = models.OneToOneField(EntranceBookletDetail, related_name="tag_package")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(default=datetime.now)
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    content = models.TextField()
    q_count = models.PositiveIntegerField()
    is_changed = models.BooleanField(default=False)

    stats = GenericRelation(ConcoughProductStatistic, related_query_name="entrance_tags",
                            content_type_field='target_ct_id',
                            object_id_field='target_id',
                            )
    purchase = GenericRelation(ConcoughUserPurchased, related_query_name="entrance_tags",
                               content_type_field='target_ct_id',
                               object_id_field='target_id',
                               )

    def __unicode__(self):
        return "tag package: {} for {}".format(self.unique_key, self.booklet_detail)


class EntranceTagSaleData(models.Model):
    entrance_type = models.ForeignKey(EntranceType, related_name="tags_sale_data")
    cost = models.IntegerField(blank=False, default=0)
    updated = models.DateTimeField(auto_now=True)
    year = models.IntegerField()
    month = models.IntegerField()
    q_count = models.SmallIntegerField(default=ENTRANCE_TAG_SALE_Q_COUNT)

    def __unicode__(self):
        return u"%s (%4d/%2d) for %d - %d" % (self.entrance_type, self.year, self.month, self.q_count, self.cost,)

