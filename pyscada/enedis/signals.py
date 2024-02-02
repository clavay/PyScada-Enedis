# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.enedis.models import (
    SGETiersDevice,
    SGETiersVariable,
    SGETiersField,
)

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.core.exceptions import FieldError

from slugify import slugify
from time import sleep
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SGETiersDevice)
@receiver(post_save, sender=SGETiersVariable)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is SGETiersDevice:
        post_save.send_robust(sender=Device, instance=instance.sgetiers_device)
    elif type(instance) is SGETiersVariable:
        post_save.send_robust(sender=Variable, instance=instance.sgetiers_variable)


@receiver(post_delete, sender=SGETiersDevice)
def _del_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is SGETiersDevice:
        try:
            logger.debug("Enedis signal post delete")
            if instance.parent_device() is not None:
                instance.parent_device().delete()
        except Exception as e:
            logger.info(e)


@receiver(m2m_changed, sender=SGETiersDevice.auto_create_variables.through)
def create_all_variables(sender, instance, **kwargs):
    if "action" in kwargs and kwargs["action"] == "post_add" and "pk_set" in kwargs:
        for field_id in kwargs["pk_set"]:
            var = SGETiersField.objects.get(id=field_id)
            try:
                v, c = Variable.objects.update_or_create(
                    device=instance.sgetiers_device,
                    name=slugify(f"{instance.sgetiers_device} {var.label}"),
                    defaults={
                        "cov_increment": -1,
                        "description": var.label,
                        "unit": var.unit,
                    },
                )
                sge_var = SGETiersVariable.objects.update_or_create(
                    sgetiers_variable=v,
                    defaults={
                        "command_service_type": var.command_service_type,
                        "xml_path": var.xml_path,
                    },
                )
                logger.debug(
                    f"Auto created SGETiers variable {var.label} for device {instance.sgetiers_device}"
                )
            except (FieldError, ValueError) as e:
                logger.warning(e)
