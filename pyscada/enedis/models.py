# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, DeviceHandler, DeviceProtocol
from pyscada.models import Variable, VariableProperty, Unit
from . import PROTOCOL_ID

from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import FieldError
from django.forms.models import BaseInlineFormSet
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)

# list of services from https://github.com/lowatt/lowatt-enedis/blob/master/lowatt_enedis/services.py
# get it in python with :
# import lowatt_enedis
# lowatt_enedis.COMMAND_SERVICE.keys()
command_service_type_choices = (
    ("technical", "Donnnées techniques contractuelles"),
    ("detailsV3", "Mesures détaillées"),
)


class SGETiersField(models.Model):
    label = models.CharField(
        max_length=254,
    )
    xml_path = models.TextField()
    command_service_type = models.CharField(
        max_length=250, choices=command_service_type_choices
    )
    unit = models.ForeignKey(Unit, on_delete=models.SET(1))

    def __str__(self):
        return f"{self.label} ({self.command_service_type})"


class SGETiersDevice(models.Model):
    sgetiers_device = models.OneToOneField(
        Device, null=True, blank=True, on_delete=models.CASCADE
    )
    login = models.EmailField(
        max_length=254,
        blank=True,
    )
    certificat = models.FilePathField(
        path="/home/pyscada/enedisCertificates",
        max_length=254,
        blank=True,
    )
    private_key = models.FilePathField(
        path="/home/pyscada/enedisCertificates",
        max_length=254,
        blank=True,
    )
    pdl = models.PositiveBigIntegerField(blank=True)
    authorization = models.BooleanField(default=False)
    initialized = models.BooleanField(default=False)
    auto_create_variables = models.ManyToManyField(
        SGETiersField,
        blank=True,
    )

    protocol_id = PROTOCOL_ID

    filter_horizontal = ("auto_create_variables",)

    def clean(self):
        super().clean()
        if self.pdl is None:
            raise ValidationError("Enter a PDL.")
        if self.login == "":
            raise ValidationError("Enter a login.")
        if self.certificat == "":
            raise ValidationError(
                "Choose a certificate from the /home/pyscada/enedisCertificates folder."
            )
        if self.private_key == "":
            raise ValidationError(
                "Choose a private key from the /home/pyscada/enedisCertificates folder."
            )

    def parent_device(self):
        try:
            return self.sgetiers_device
        except:
            return None

    def __str__(self):
        return self.sgetiers_device.short_name

    def save(self, *args, **kwargs):
        self.initialized = False
        super().save(*args, **kwargs)
        d = None
        if self.sgetiers_device is not None:
            if (
                type(Device.polling_interval_choices) == tuple
                and (86400.0, "1 Day") in Device.polling_interval_choices
            ):
                poll = 86400.0
            else:
                poll = 3600.0

            # Create the Device
            d = self.sgetiers_device
            d.polling_interval = poll
            d.save()

    class FormSet(BaseInlineFormSet):
        def add_fields(self, form, index):
            super().add_fields(form, index)
            form.fields["initialized"].disabled = True


class SGETiersVariable(models.Model):
    sgetiers_variable = models.OneToOneField(
        Variable, null=True, blank=True, on_delete=models.CASCADE
    )
    command_service_type = models.CharField(
        max_length=250, choices=command_service_type_choices
    )
    xml_path = models.TextField()
    found_in_last_request = models.BooleanField(default=False)
