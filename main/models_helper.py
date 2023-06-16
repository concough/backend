# coding=utf-8
__author__ = 'abolfazl'

from django.db.models import FileField, ImageField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.core.files import storage


class NoDeleteFileStorage(storage.FileSystemStorage):
    def delete(self, name):
        pass


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types.
        Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file
        size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """

    content_types = []
    max_upload_size = 2621440

    def __init__(self, content_types=[], max_upload_size=2621440, *args, **kwargs):
        self.content_types = content_types
        self.max_upload_size = max_upload_size

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(u'حداکثر حجم فایل ' + filesizeformat(self.max_upload_size) +
                                                u' می باشد. حجم فایل بارگذاری شده: ' + filesizeformat(file._size)
                    )
            else:
                raise forms.ValidationError(u'فرمت فایل اشتباه است', code='wrongformat')
        except AttributeError:
            pass

        return data


class ContentTypeRestrictedImageField(ImageField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types.
        Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file
        size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """

    content_types = []
    max_upload_size = 2621440

    def __init__(self, content_types=[], max_upload_size=2621440, *args, **kwargs):
        self.content_types = content_types
        self.max_upload_size = max_upload_size

        super(ContentTypeRestrictedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedImageField, self).clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(u'حداکثر حجم فایل ' + filesizeformat(self.max_upload_size) +
                                                u' می باشد. حجم فایل بارگذاری شده: ' + filesizeformat(file._size)
                    )
            else:
                raise forms.ValidationError(u'فرمت فایل اشتباه است', code='wrongformat')
        except AttributeError:
            pass

        return data



