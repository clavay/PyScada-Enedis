# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.db.utils import ProgrammingError, OperationalError

from . import __app_name__

import logging

logger = logging.getLogger(__name__)


class PyScadaEnedisConfig(AppConfig):
    name = "pyscada." + __app_name__.lower()
    verbose_name = _("PyScada " + __app_name__)
    path = os.path.dirname(os.path.realpath(__file__))
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        __import__("pyscada." + __app_name__.lower() + ".signals")

        # create the /home/pyscada/enedisCertificates dorectory for cetificates and keys
        try:
            cert_path = "/home/pyscada/enedisCertificates"
            if not os.path.exists(cert_path):
                os.mkdir(cert_path)
        except Exception as e:
            logger.warning(e)

        try:
            from pyscada.models import Unit, DeviceHandler

            enedis_handler = DeviceHandler.objects.get_or_create(
                name="EnedisHandler",
                defaults={"handler_class": "pyscada.enedis.devices.enedis"},
            )
            if enedis_handler[1]:
                logger.info("Enedis Handler created.")

            unit_blank = Unit.objects.get_or_create(
                unit="",
                defaults={"description": "", "udunit": ""},
            )[0]
            unit_kwh = Unit.objects.get_or_create(
                unit="kWh",
                defaults={"description": "kilowatthour", "udunit": "kilowatthour"},
            )[0]
            unit_wh = Unit.objects.get_or_create(
                unit="Wh",
                defaults={"description": "watthour", "udunit": "watthour"},
            )[0]
            unit_w = Unit.objects.get_or_create(
                unit="W",
                defaults={"description": "watt", "udunit": "watt"},
            )[0]
            unit_kva = Unit.objects.get_or_create(
                unit="kVA",
                defaults={"description": "kilovoltampere", "udunit": "kilovoltampere"},
            )[0]

            # list of [label, command_service_type, xml_path, unit]
            default_sge_tiers_fields = [
                # donneesGenerales
                [
                    "Code postal",
                    "technical",
                    ".//donneesGenerales/adresseInstallation/codePostal",
                    unit_blank,
                ],
                [
                    "Escalier / Etage / Appartement",
                    "technical",
                    ".//donneesGenerales/adresseInstallation/escalierEtEtageEtAppartement",
                    unit_blank,
                ],
                [
                    "Batiment",
                    "technical",
                    ".//donneesGenerales/adresseInstallation/batiment",
                    unit_blank,
                ],
                [
                    "Numéro / Nom Voie",
                    "technical",
                    ".//donneesGenerales/adresseInstallation/numeroEtNomVoie",
                    unit_blank,
                ],
                [
                    "Lieu dit",
                    "technical",
                    ".//donneesGenerales/adresseInstallation/LieuDit",
                    unit_blank,
                ],
                [
                    "Commune",
                    "technical",
                    ".//donneesGenerales/adresseInstallation/commune/libelle",
                    unit_blank,
                ],
                [
                    "Etat contractuel",
                    "technical",
                    ".//donneesGenerales/etatContractuel/libelle",
                    unit_blank,
                ],
                [
                    "Date derniere modification formule tarifaire",
                    "technical",
                    ".//donneesGenerales/dateDerniereModificationFormuleTarifaireAcheminement",
                    unit_blank,
                ],
                [
                    "Date derniere augementation puissance souscrite",
                    "technical",
                    ".//donneesGenerales/dateDerniereAugmentationPuissanceSouscrite",
                    unit_blank,
                ],
                [
                    "Segment",
                    "technical",
                    ".//donneesGenerales/segment/libelle",
                    unit_blank,
                ],
                [
                    "Niveau ouverture services",
                    "technical",
                    ".//donneesGenerales/niveauOuvertureServices",
                    unit_blank,
                ],
                # situationAlimentation
                [
                    "Domaine tension",
                    "technical",
                    ".//situationAlimentation/alimentationPrincipale/domaineTension/libelle",
                    unit_blank,
                ],
                [
                    "Tension livraison",
                    "technical",
                    ".//situationAlimentation/alimentationPrincipale/tensionLivraison/libelle",
                    unit_blank,
                ],
                [
                    "Puissance de raccordement",
                    "technical",
                    ".//situationAlimentation/alimentationPrincipale/puissanceRaccordementSoutirage",
                    unit_kva,
                ],
                [
                    "Mode après compteur",
                    "technical",
                    ".//situationAlimentation/alimentationPrincipale/tensionLivraison/libelle",
                    unit_blank,
                ],
                # situation comptage
                [
                    "Mode relevé",
                    "technical",
                    ".//situationComptage/modereleve/libelle",
                    unit_blank,
                ],
                [
                    "Media relevé",
                    "technical",
                    ".//situationComptage/mediareleve/libelle",
                    unit_blank,
                ],
                [
                    "futures plages heures creuses",
                    "technical",
                    ".//situationComptage/futuresPlagesHeuresCreuses/libelle",
                    unit_blank,
                ],
                [
                    "Type comptage",
                    "technical",
                    ".//situationComptage/dispositifComptage/typeComptage/libelle",
                    unit_blank,
                ],
                [
                    "Localisation compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/localisation/libelle",
                    unit_blank,
                ],
                [
                    "Matricule compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/matricule",
                    unit_blank,
                ],
                [
                    "TIC activée compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/ticActivee",
                    unit_blank,
                ],
                [
                    "TIC standard compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/ticStandard",
                    unit_blank,
                ],
                [
                    "TIC activable compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/ticActivable",
                    unit_blank,
                ],
                [
                    "Plage heures creuses compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/plagesHeuresCreuses",
                    unit_blank,
                ],
                [
                    "Numéro téléphone téléaccès compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/parametresTeleAcces/numeroTelephone",
                    unit_blank,
                ],
                [
                    "Voie aiguillage téléaccès compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/parametresTeleAcces/numeroVoieAiguillage",
                    unit_blank,
                ],
                [
                    "Etat ligne téléaccès compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/parametresTeleAcces/etatLigneTelephonique",
                    unit_blank,
                ],
                [
                    "Clé téléaccès compteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/compteurs/compteur/parametresTeleAcces/cle",
                    unit_blank,
                ],
                [
                    "Disjoncteur",
                    "technical",
                    ".//situationComptage/dispositifComptage/disjoncteur/calibre/libelle",
                    unit_blank,
                ],
                [
                    "Plage heures creuses",
                    "technical",
                    ".//situationComptage/dispositifComptage/relais/plageHeuresCreuses",
                    unit_blank,
                ],
                [
                    "Calibre transformateur",
                    "technical",
                    ".//situationComptage/dispositifComptage/transformateurCourant/calibre/libelle",
                    unit_blank,
                ],
                [
                    "Couplage transformateur",
                    "technical",
                    ".//situationComptage/dispositifComptage/transformateurCourant/couplage/libelle",
                    unit_blank,
                ],
                [
                    "Classe Precision transformateur",
                    "technical",
                    ".//situationComptage/dispositifComptage/transformateurCourant/classePrecision/libelle",
                    unit_blank,
                ],
                [
                    "Position transformateur",
                    "technical",
                    ".//situationComptage/dispositifComptage/transformateurCourant/position/libelle",
                    unit_blank,
                ],
                [
                    "Calibre Tension transformateur",
                    "technical",
                    ".//situationComptage/dispositifComptage/transformateurCourant/calibre/libelle",
                    unit_blank,
                ],
                # situation contractuelle
                [
                    "Calendrier Frn",
                    "technical",
                    ".//situationContractuelle/structureTarifaire/calendrierFrn/libelle",
                    unit_blank,
                ],
                # ["Formule tarifaire", "technical", ".//situationContractuelle/structureTarifaire/formuleTarifaireAcheminement/libelle", unit_blank],
                [
                    "Formule tarifaire",
                    "technical",
                    ".//situationContractuelle/structureTarifaire/puissanceSouscriteMax/valeur",
                    unit_kva,
                ],
                # time series
                [
                    "Courbes puissances",
                    "detailsV3-COURBE-PA",
                    ".//grandeur/points",
                    unit_w,
                ],  #    default_inputs["type"]='COURBE',default_inputs["courbe_type"]='PA'  / date:  .//grandeur/points/d
                [
                    "Courbes énergie active",
                    "detailsV3-ENERGIE-EA",
                    ".//grandeur/points",
                    unit_wh,
                ],  #    default_inputs["type"]='ENERGIE',default_inputs["courbe_type"]='EA'  / date:  .//cadranTotalisateur/valeur/d
                [
                    "Courbes énergie réactive",
                    "detailsV3-ENERGIE-ER",
                    ".//grandeur/points",
                    unit_wh,
                ],  #    default_inputs["type"]='ENERGIE',default_inputs["courbe_type"]='ER'  / date:  .//cadranTotalisateur/valeur/d
                [
                    "Courbes index HC",
                    "detailsV3-INDEX-HC",
                    ".//calendrier/classeTemporelle/[idClasseTemporelle='HC']/valeur",
                    unit_wh,
                ],  #    default_inputs["type"]='ENERGIE',default_inputs["courbe_type"]='ER'  / date:  .//cadranTotalisateur/valeur/d
                [
                    "Courbes index HP",
                    "detailsV3-INDEX-HP",
                    ".//calendrier/classeTemporelle/[idClasseTemporelle='HP']/valeur",
                    unit_wh,
                ],  #    default_inputs["type"]='ENERGIE',default_inputs["courbe_type"]='ER'  / date:  .//cadranTotalisateur/valeur/d
            ]

            from .models import SGETiersField

            for item in default_sge_tiers_fields:
                try:
                    f, created = SGETiersField.objects.update_or_create(
                        xml_path=item[2],
                        command_service_type=item[1],
                        defaults={"label": item[0], "unit": item[3]},
                    )
                    if created:
                        logger.info(f"SGETiersField created : {item}")
                except SGETiersField.MultipleObjectsReturned:
                    logger.warning(f"Multiple SGETiersField for {item}")
                    SGETiersField.objects.filter(
                        id__in=list(
                            SGETiersField.objects.filter(
                                command_service_type=item[1],
                                xml_path=item[2],
                            ).values_list(flat=True)[1:]
                        )
                    ).delete()
        except ProgrammingError:
            pass
        except OperationalError:
            pass
