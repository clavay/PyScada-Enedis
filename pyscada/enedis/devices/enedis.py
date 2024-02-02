# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import json
from time import sleep, time
from pytz import timezone, utc
from pytz.exceptions import AmbiguousTimeError

import lowatt_enedis
import lowatt_enedis.services
import defusedxml.ElementTree as ET
from xml.sax._exceptions import SAXParseException

import logging

logger = logging.getLogger(__name__)

if os.getenv("DJANGO_SETTINGS_MODULE") is not None:
    try:
        from . import GenericDevice
        from pyscada.models import VariableProperty, Variable
    except:
        logger.info("Run this file from the parent directory")
        print("Run this file from the parent directory")
else:
    import sys

    logger.info("Django settings not configured.")
    GenericDevice = object
    logging.basicConfig(
        level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)]
    )

"""Object based access to the Enedis API
Example:

import sys
sys.path.append(".")
from enedis import SGETiers
import rich
import json
import lowatt_enedis
import xml.etree.ElementTree as ET
TOKEN='your_token'
LOGIN='your_login'
CERT='/cert/file/path'
KEY='/key/file/path'
PROXY='sge-b2b.enedis.fr'
CONTRACT='your_contract'
HOMOLOGATION=False

PRM='your_prm'

#Default inputs
default_inputs={
    'prm':PRM,
    'autorisation': True,
    'cadre': "ACCORD_CLIENT",
    'type': 'INDEX',
    'from': '2023-12-09',
    'to': '2023-12-13',
    "corrigee": False,
}

e=SGETiers(login=LOGIN, fullchain_certificate_file=CERT, private_key_file=KEY, contract=CONTRACT, homologation=HOMOLOGATION)

command_service='technical'
print(command_service)
e.set_client(command_service=command_service)
r=e.send_request(input_dict=default_inputs)
#rich.print_json(json.dumps(r, indent=2, default=lowatt_enedis.json_encode_default, sort_keys=True))
rich.print(lowatt_enedis.pretty_xml(r.decode()))
root = ET.fromstring(r)
commune = root.findall(".//donneesGenerales/adresseInstallation/commune/libelle")
print(f"Commune : {commune[0].text}")

command_service='detailsV3'
print(f"{command_service} {default_inputs['type']}")
e.set_client(command_service=command_service)
r=e.send_request(input_dict=default_inputs)
#rich.print_json(json.dumps(r, indent=2, default=lowatt_enedis.json_encode_default, sort_keys=True))
rich.print(lowatt_enedis.pretty_xml(r.decode()))
root = ET.fromstring(r)
date0 = root.findall(".//cadranTotalisateur/valeur/d")
index0 = root.findall(".//cadranTotalisateur/valeur/v")
print(f"Index : {date0[0].text} {index0[0].text}")

default_inputs['type'] = 'COURBE'
default_inputs['courbe_type'] = 'PA'
command_service='detailsV3'
print(f"{command_service} {default_inputs['type']}")
e.set_client(command_service=command_service)
r=e.send_request(input_dict=default_inputs)
#rich.print_json(json.dumps(r, indent=2, default=lowatt_enedis.json_encode_default, sort_keys=True))
rich.print(lowatt_enedis.pretty_xml(r.decode()))
root = ET.fromstring(r)
date0 = root.findall(".//grandeur/points/d")
index0 = root.findall(".//grandeur/points/v")
print(f"Index : {date0[0].text} {index0[0].text}")
"""

__author__ = "Camille Lavayssière"
__copyright__ = "Copyright 2023, Université de Pau et des Pays de l'Adour"
__credits__ = []
__license__ = "AGPLv3"
__version__ = "0.1.0"
__maintainer__ = "Camille Lavayssière"
__email__ = "clavayssiere@univ-pau.fr"
__status__ = "Beta"
__docformat__ = "reStructuredText"


class SGETiers(object):
    def __init__(
        self,
        fullchain_certificate_file="/root/cert.pem",
        private_key_file="/root/key.pem",
        proxy_url="sge-b2b.enedis.fr",
        token="",
        login=None,
        contract="",
        homologation=False,
        timeout=10,
    ):
        self.certificate_file = fullchain_certificate_file
        self.key_file = private_key_file
        self.proxy_url = proxy_url
        self.token = token
        self.login = login
        self.contract = contract
        self.homologation = homologation
        self.timeout = timeout
        self.command_service = None

    def set_client(self, command_service="technical"):
        self.command_service = command_service
        self.c = command_service.split("-")[0]
        self.client = lowatt_enedis.get_client(
            lowatt_enedis.COMMAND_SERVICE[self.c][0],
            self.certificate_file,
            self.key_file,
            self.homologation,
        )

        # return as XML
        self.client.options.retxml = True

        # replace enedis url by the proxy url and token
        for method in lowatt_enedis.iter_methods(self.client):
            if self.homologation:
                token = f"{self.token}_homologation"
                method.location = method.location.replace(
                    b"sge-homologation-b2b.enedis.fr",
                    f"{self.proxy_url}/{token}".encode(),
                )
            else:
                token = self.token
                # print(method.location.decode("utf-8"))
                # method.location = method.location.replace(
                #    b"sge-b2b.enedis.fr",
                #    f"{self.proxy_url}/{token}".encode("utf-8"),
                # )
                # print(method.location)
        return True

    def send_request(self, input_dict):
        result = None
        try:
            if self.c in lowatt_enedis.COMMAND_SERVICE:
                if "login" not in input_dict:
                    input_dict["login"] = self.login

                r = lowatt_enedis.COMMAND_SERVICE[self.c][2](self.client, input_dict)
                return r
            else:
                result = f"{self.c} command service does not exist."
        except (lowatt_enedis.WSException, SAXParseException, Exception) as e:
            result = e
        logger.info(f"{input_dict} {result}")
        return result


class Handler(GenericDevice):
    """
    Enedis API and other API with the same command set
    """

    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self.variables_dict = {}
        self.inst = None
        self.inputs = {}

    def connect(self):
        if hasattr(self._device, "sgetiersdevice"):
            self.inst = SGETiers(
                login=self._device.sgetiersdevice.login,
                fullchain_certificate_file=self._device.sgetiersdevice.certificat,
                private_key_file=self._device.sgetiersdevice.private_key,
                homologation=False,
            )
            return True
        else:
            logger.info(f"Cannot connect to SGETiers device {self._device}")
            return False

    def before_read(self):
        """
        group the variable to read by command service
        """

        if self.inst is None and not self.connect():
            return False

        self.command_service_type = {}
        for var in self.variables_dict:
            if not hasattr(self.variables_dict[var], "sgetiersvariable"):
                logger.info(
                    f"Enedis handler cannot read data for non sgetiers variable as {var}"
                )
            if (
                self.variables_dict[var].sgetiersvariable.command_service_type
                not in self.command_service_type
            ):
                self.command_service_type[
                    self.variables_dict[var].sgetiersvariable.command_service_type
                ] = []
            self.command_service_type[
                self.variables_dict[var].sgetiersvariable.command_service_type
            ].append(var)

        return True

    def after_read(self):
        self.variables_dict = {}

    def read_data_all(self, variables_dict):
        output = []

        self.variables_dict = variables_dict

        if self.before_read():
            for command_service in self.command_service_type:
                service_read = self._read_service(command_service)
                if service_read:
                    output += service_read
        logger.info(output)

        self.after_read()
        return output

    def _read_service(self, command_service):
        self.inst.set_client(command_service=command_service)
        accord_client = (
            "ACCORD_CLIENT" if self._device.sgetiersdevice.authorization else ""
        )

        self.inputs = {
            "login": self._device.sgetiersdevice.login,
            "prm": self._device.sgetiersdevice.pdl,
            "autorisation": self._device.sgetiersdevice.authorization,
            "cadre": accord_client,
            "corrigee": False,
        }
        if command_service == "technical":
            return self._read_technical()
        if command_service == "detailsV3-COURBE-PA":
            return self._read_detailsV3_grandeur_points(
                "COURBE", "PA", "detailsV3-COURBE-PA"
            )
        if command_service == "detailsV3-ENERGIE-EA":
            return self._read_detailsV3_grandeur_points(
                "ENERGIE", "EA", "detailsV3-ENERGIE-EA"
            )
        if command_service == "detailsV3-ENERGIE-ER":
            return self._read_detailsV3_grandeur_points(
                "ENERGIE", "ER", "detailsV3-ENERGIE-ER"
            )
        if command_service == "detailsV3-INDEX-HC":
            return self._read_detailsV3_grandeur_points(
                "INDEX", "HC", "detailsV3-INDEX-HC"
            )
        if command_service == "detailsV3-INDEX-HP":
            return self._read_detailsV3_grandeur_points(
                "INDEX", "HP", "detailsV3-INDEX-HP"
            )

    def _read_technical(self):
        output = []
        read_time = time()
        for i in range(0, 10):
            # try 10 times max
            try:
                r = self.inst.send_request(input_dict=self.inputs)
                root = ET.fromstring(r)
            except Exception as e:
                logger.info(f"Read technical failed {i} for {self._device} : {e}")
                sleep(2)
            else:
                for var_id in self.command_service_type["technical"]:
                    if var_id not in self._variables:
                        logger.warning(f"Variable {var_id} not in self.variables")
                    if var_id not in self.variables_dict:
                        logger.warning(f"Variable {var_id} not in self.variables_dict")
                    var = self.variables_dict[var_id]
                    sgetiers_var = var.sgetiersvariable
                    value = root.findall(sgetiers_var.xml_path)
                    if len(value) == 0:
                        logger.warning(
                            f"Variable {var} not found in technical data ({sgetiers_var.xml_path})"
                        )
                        continue
                    elif len(value) > 1:
                        logger.info(
                            "Variable {var} found more than one time in technical data ({sgetiers_var.xml_path})"
                        )
                    value = value[0].text
                    if (
                        value is not None
                        and value != ""
                        and var.update_values([value], [read_time])
                    ):
                        output.append(var)
                break
        return output

    def _read_detailsV3_grandeur_points(
        self, command_type, courbe_type, command_service
    ):
        self.inputs["type"] = command_type
        self.inputs["courbe_type"] = courbe_type
        months_offset_max = 24
        if "COURBE" not in command_service:
            months_offset_max = 36
        t_from = date.fromtimestamp(
            self._get_min_time_for_command_service_type(
                command_service, months_offset_max
            )
        )
        logger.info(f"Starting to read {command_service} from {t_from}")
        stop = False
        variables_values = {}
        variables_timestamps = {}
        output = []
        while not stop:
            t_to = t_from + timedelta(days=6)
            if "COURBE" not in command_service:
                t_to = date.today()
            if t_to > (date.today() - timedelta(days=1)):
                stop = True
                t_to = date.today() - timedelta(days=1)
            if t_to == t_from:
                break
            self.inputs["from"] = t_from.isoformat()
            self.inputs["to"] = t_to.isoformat()
            for i in range(0, 10):
                # try 10 times max
                logger.info(self.inputs)
                try:
                    r = self.inst.send_request(input_dict=self.inputs)
                    root = ET.fromstring(r)
                except TypeError as e:
                    if "SGT4" in str(r):
                        logger.info(f"Functionnal Error : {self.inputs} {e} {r}")
                        break
                    elif "SGT589" in str(r):
                        logger.info(f"Technical Error : {self.inputs} {e} {r}")
                        stop = True
                        break
                    elif "SGT5" in str(r):
                        logger.info(f"Technical Error : {self.inputs} {e} {r}")
                    else:
                        logger.info(f"Unknown error : {self.inputs} {e} {r}")

                except Exception as e:
                    logger.warning(
                        f"Read {command_service} failed {i} for {self._device} : {e}"
                    )
                    sleep(2)
                else:
                    for var_id in self.command_service_type[command_service]:
                        if var_id not in self._variables:
                            logger.warning(f"Variable {var_id} not in self.variables")
                        if var_id not in self.variables_dict:
                            logger.warning(
                                f"Variable {var_id} not in self.variables_dict"
                            )
                        var = self.variables_dict[var_id]
                        sgetiers_var = var.sgetiersvariable
                        result = root.findall(sgetiers_var.xml_path)
                        if len(result) == 0:
                            logger.warning(
                                f"Variable {var} not found in detailed V3({sgetiers_var.xml_path})"
                            )
                            continue
                        if var_id not in variables_values:
                            variables_values[var_id] = []
                            variables_timestamps[var_id] = []
                        for r in result:
                            try:
                                d = r.findall("d")
                                if len(d) == 0:
                                    logger.warning(
                                        f"date not found in detailsV3 Courbe PA"
                                    )
                                    continue
                                if len(d) > 1:
                                    logger.warning(
                                        f"more than one date found in detailsV3 Courbe PA"
                                    )
                                d = datetime.fromisoformat(d[0].text)
                                paris = timezone("Europe/Paris")
                                try:
                                    d = paris.localize(d, is_dst=None).astimezone(utc)
                                except AmbiguousTimeError:
                                    # date time is at the daylight saving time (summer/winter change), not possible to determine, set -1h offset
                                    d -= timedelta(seconds=3600)
                                d = d.timestamp()
                            except ValueError:
                                logger.warning(
                                    f"Reading {var} - date format from SGETiers invalid for detailsV3 Courbe PA : {date_list[i].text}"
                                )
                                continue
                            v = r.findall("v")
                            if len(v) == 0:
                                logger.warning(
                                    f"value not found in detailsV3 Courbe PA"
                                )
                                continue
                            if len(v) > 1:
                                logger.warning(
                                    f"more than one value found in detailsV3 Courbe PA"
                                )
                            v = v[0].text
                            variables_values[var_id].append(v)
                            variables_timestamps[var_id].append(d)
                        logger.info(f"{var} length : {len(variables_values[var_id])}")
                    break
            t_from = t_to
        for var_id in self.command_service_type[command_service]:
            var = self.variables_dict[var_id]
            if var_id in variables_values and var.update_values(
                variables_values[var_id], variables_timestamps[var_id]
            ):
                output.append(var)
            logger.info(len(output))
        return output

    def _get_min_time_for_command_service_type(
        self, command_service, months_offset_max=24
    ):
        time_min = time()
        logger.info(command_service)
        for var_id in self.command_service_type[command_service]:
            if self.variables_dict[var_id].query_prev_value():
                time_min = min(time_min, self.variables_dict[var_id].timestamp_old)
            else:
                time_min = (
                    datetime.today()
                    - relativedelta(months=months_offset_max)
                    + relativedelta(days=1)
                ).timestamp()
                break
        logger.info(f"time_min : {time_min}")
        return time_min
