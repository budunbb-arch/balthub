# /opt/balthub/apps/estates/parsing/services/importer.py

from lxml import etree
from django.utils import timezone

from apps.estates.parsing.utils import (
    parse_and_resolve,
    resolve_dictionary,
    resolve_district,
    resolve_city,
    extract_deadline,
    normalize_deadline,
    generate_hash,
    extract_project_description,
    normalize_text_block,
    to_bool,
)
from apps.estates.parsing.constants import BUILDING_STATUS_MAPPING
from apps.estates.developers.models import Developer
from apps.estates.projects.models import Project, ProjectParams, ProjectDescription, ProjectImage
from apps.estates.houses.models import House, HouseParams
from apps.estates.flats.models import Flat, FlatParams, FlatDeal

from apps.core.dictionaries.models import (
    PropertyType,
    PropertyCategory,
    FinishType,
    BalconyType,
    BathroomUnitType,
    HouseStructureType,
    BuildingStatus,
    DealType,
    Currency,
)
from apps.estates.parsing.management.execution.parser_control import check_cancel
from apps.estates.parsing.management.execution.parser_cancel import ParserCancelChecker, ParserCancelled


from . import helpers
from . import images

import logging

logger = logging.getLogger(__name__)


class NMarketImporter:

    def __init__(self, feed_path, parser_run):
        self.feed_path = feed_path
        self.parser_run = parser_run

    def run(self):

        source_parser = self.parser_run.parser

        logger.warning("IMPORTER RUN STARTED")
        logger.warning(__file__)
        processed = 0

        stats = {
            "offers": 0,
            "developers_created": 0,
            "developers_updated": 0,
            "projects_created": 0,
            "projects_updated": 0,
            "houses_created": 0,
            "houses_updated": 0,
            "flats_created": 0,
            "flats_updated": 0,
        }

        cancel = ParserCancelChecker(self.parser_run)
        logger.warning("CANCEL CHECKER CREATED")

        logger.info("Unpublishing previously imported objects...")

        Developer.objects.filter(
            origin_type="parser",
            origin_parser=source_parser,
            is_public=True,
        ).update(is_public=False)

        Project.objects.filter(
            origin_type="parser",
            origin_parser=source_parser,
            is_public=True,
        ).update(is_public=False)

        House.objects.filter(
            origin_type="parser",
            origin_parser=source_parser,
            is_public=True,
        ).update(is_public=False)

        Flat.objects.filter(
            origin_type="parser",
            origin_parser=source_parser,
            is_public=True,
        ).update(is_public=False)

        logger.info("Previous objects unpublished")

        xml_parser = etree.XMLParser(recover=True)
        tree = etree.parse(str(self.feed_path), xml_parser)
        root = tree.getroot()

        ns = {"y": "http://webmaster.yandex.ru/schemas/feed/realty/2010-06"}

        for offer in root.findall("y:offer", ns):

            processed += 1

            cancel.tick()

            description = helpers.get_text(offer, "y:description", ns)

            # ------------------------
            # IMAGES PARSING (СНАЧАЛА!)
            # ------------------------
            offer_images = offer.findall("y:image", ns)

            flat_plan = None
            house_image = None
            house_plan = None
            project_images = []

            for img in offer_images:
                url = img.text.strip() if img.text else None
                tag = img.get("tag")

                if not url:
                    continue

                if tag == "plan":
                    flat_plan = url

                elif tag == "housemain":
                    house_image = url

                elif tag == "floorplan":
                    house_plan = url

                else:
                    project_images.append(url)

            # download images to local media storage
            flat_plan = images.download_image(flat_plan, "flat_plans") or flat_plan
            house_image = images.download_image(house_image, "houses") or house_image
            house_plan = images.download_image(house_plan, "house_plans") or house_plan

            # убрать дубли URL из фида
            project_images = list(dict.fromkeys(project_images))

            # скачать изображения
            project_images = [
                images.download_image(url, "project_images") or url
                for url in project_images
            ]

            # убрать дубли после скачивания
            project_images = list(dict.fromkeys(project_images))

            # ------------------------
            # DEVELOPER
            # ------------------------
            developer, created = parse_and_resolve(
                Developer,
                description,
                patterns=[
                    r"Застройщик:\s*(.+?)(?:\.\s|$)",
                    r"Застройщик\s*-\s*(.+?)(?:\.\s|$)",
                ],
                normalize_rules=[],
            )

            helpers.touch_instance(
                developer,
                created,
                stats,
                "developers_created",
                "developers_updated",
                origin_parser=source_parser,
                is_public=True,
                published_at=developer.published_at or timezone.now(),
            )

            # ------------------------
            # PROJECT
            # ------------------------
            project, created = Project.objects.get_or_create(
                external_id=helpers.get_text(offer, "y:nmarket-complex-id", ns),
                defaults={
                    "name": helpers.get_text(offer, "y:building-name", ns),
                    "developer": developer,
                    "is_public": True,
                    "published_at": timezone.now(),
                }
            )

            helpers.touch_instance(
                project,
                created,
                stats,
                "projects_created",
                "projects_updated",
                origin_parser=source_parser,
                is_public=True,
                published_at=project.published_at or timezone.now(),
                developer=developer,
            )


            # ------------------------
            # PROJECT DESCRIPTION
            # ------------------------
            project_description_text = extract_project_description(description)

            if project_description_text:
                project_description_text = normalize_text_block(project_description_text)
                
                description_hash = generate_hash(project_description_text)

                obj, created = ProjectDescription.objects.get_or_create(
                    project=project,
                    defaults={
                        "description": project_description_text,
                        "hash": description_hash
                    }
                )

                # если уже есть — обновляем только если hash изменился
                if not created and obj.hash != description_hash:
                    obj.description = project_description_text
                    obj.hash = description_hash
                    obj.save(update_fields=["description", "hash"])


            # PROJECT PARAMS
            city = resolve_city(
                helpers.get_nested_text(offer, "y:location/y:locality-name", ns)
            )

            district = resolve_district(
                city,
                helpers.get_nested_text(offer, "y:location/y:district", ns),
            ) if city else None

            helpers.update_or_create_changed(
                ProjectParams,
                {"project": project},
                {
                    "city": city,
                    "district": district,
                    "property_type": resolve_dictionary(
                        PropertyType,
                        helpers.get_text(offer, "y:property-type", ns)
                    ),
                    "property_category": resolve_dictionary(
                        PropertyCategory,
                        helpers.get_text(offer, "y:category", ns)
                    ),
                }
            )

            # PROJECT IMAGES SYNC

            incoming_images = set(filter(None, project_images))

            ProjectImage.objects.filter(
                project=project
            ).exclude(
                image__in=incoming_images
            ).delete()

            for image_url in incoming_images:
                ProjectImage.objects.get_or_create(
                    project=project,
                    image=image_url
                )

            # ------------------------
            # HOUSE
            # ------------------------
            external_id=helpers.get_text(offer, "y:nmarket-building-id", ns)

            house, created = House.objects.get_or_create(
                external_id=external_id,
                defaults={
                    "project": project,
                    "is_public": True,
                }
            )

            helpers.touch_instance(
                house,
                created,
                stats,
                "houses_created",
                "houses_updated",
                origin_parser=source_parser,
                project=project,
                image=house_image or house.image,
                plan=house_plan or house.plan,
                is_public=True,
            )

            # HOUSE PARAMS
            deadline_raw = extract_deadline(description)
            deadline = normalize_deadline(deadline_raw)

            helpers.update_or_create_changed(
                HouseParams,
                {"house": house},
                {
                    "address": helpers.get_nested_text(offer, "y:location/y:address", ns),
                    "corpus": helpers.get_text(offer, "y:building-section", ns),
                    "phase": helpers.get_text(offer, "y:building-phase", ns),
                    "deadline": deadline,
                    "deadline_year": helpers.to_int(
                        helpers.get_text(offer, "y:built-year", ns)
                    ),
                    "floors": helpers.to_int(helpers.get_text(offer, "y:floors-total", ns)),
                    "house_structure_type": resolve_dictionary(
                        HouseStructureType,
                        helpers.get_text(offer, "y:building-type", ns),
                    ),
                    "building_status": resolve_dictionary(
                        BuildingStatus,
                        helpers.get_text(offer, "y:building-state", ns),
                        mapping=BUILDING_STATUS_MAPPING
                    ),
                    "lift": to_bool(helpers.get_text(offer, "y:lift", ns)),
                    "parking": to_bool(helpers.get_text(offer, "y:parking", ns)),
                    "latitude": helpers.to_float(
                        helpers.get_nested_text(offer, "y:location/y:latitude", ns)
                    ),
                    "longitude": helpers.to_float(
                        helpers.get_nested_text(offer, "y:location/y:longitude", ns)
                    ),
                }
            )

            # ------------------------
            # FLAT
            # ------------------------
            apartment = helpers.get_nested_text(offer, "y:location/y:apartment", ns)

            flat, created = Flat.objects.get_or_create(
                external_id=offer.get("internal-id"),
                defaults={
                    "house": house,
                    "number": apartment.strip() if apartment else None,
                    "plan": flat_plan,
                    "is_public": True,
                },
            )

            helpers.touch_instance(
                flat,
                created,
                stats,
                "flats_created",
                "flats_updated",
                origin_parser=source_parser,
                house=house,
                number=apartment.strip() if apartment else None,
                plan=flat_plan,
                is_public=True,
            )

            helpers.update_or_create_changed(
                FlatParams,
                {"flat": flat},
                {
                    "rooms": helpers.to_int(helpers.get_text(offer, "y:rooms", ns)),
                    "rooms_alias": f"{helpers.get_text(offer, 'y:rooms', ns)}к",
                    "square": helpers.to_float(
                        helpers.get_nested_text(offer, "y:area/y:value", ns)
                    ),
                    "floor": helpers.to_int(helpers.get_text(offer, "y:floor", ns)),
                    
                    "finish_type": resolve_dictionary(
                        FinishType,
                        helpers.get_text(offer, "y:renovation", ns)
                    ),
                    "balcony_type": resolve_dictionary(
                        BalconyType,
                        helpers.get_text(offer, "y:balcony", ns)
                    ),
                    "bathroom_unit_type": resolve_dictionary(
                        BathroomUnitType,
                        helpers.get_text(offer, "y:bathroom-unit", ns)
                    ),
                    "living_square": helpers.to_float(
                        helpers.get_nested_text(offer, "y:living-space/y:value", ns)
                    ),
                    "kitchen_square": helpers.to_float(
                        helpers.get_nested_text(offer, "y:kitchen-space/y:value", ns)
                    ),
                    "ceiling_height": helpers.to_float(
                        helpers.get_text(offer, "y:ceiling-height", ns)
                    ),
                }
            )

            # ------------------------
            # FLAT DEAL
            # ------------------------
            price_value = helpers.to_float(
                helpers.get_nested_text(offer, "y:price/y:value", ns)
            )

            currency_code = helpers.get_nested_text(offer, "y:price/y:currency", ns) or "RUR"
            currency = Currency.objects.filter(code__iexact=currency_code).first()

            deal_type_obj = resolve_dictionary(
                DealType,
                helpers.get_text(offer, "y:type", ns)
            )

            mortgage_value = helpers.get_text(offer, "y:mortgage", ns)
            haggle_value = helpers.get_text(offer, "y:haggle", ns)

            # создаём или обновляем сделку
            FlatDeal.objects.update_or_create(
                flat=flat,
                defaults={
                    "deal_type": deal_type_obj,
                    "price": price_value,
                    "currency": currency,
                    "mortgage": mortgage_value.lower() == "true" if mortgage_value else False,
                    "haggle": haggle_value.lower() == "true" if haggle_value else False,
                }
            )

            logger.info(
                "Flat %s imported (deal: %s)",
                flat.external_id,
                deal_type_obj,
            )

            stats["offers"] += 1

        return {
            "items_processed": processed,
            "stats": stats,
            "message": (
                f"Import completed. "
                f"Processed {processed} offers. "
                f"Developers: {stats['developers_created'] + stats['developers_updated']}, "
                f"Projects: {stats['projects_created'] + stats['projects_updated']}, "
                f"Houses: {stats['houses_created'] + stats['houses_updated']}, "
                f"Flats: {stats['flats_created'] + stats['flats_updated']}." 
            )
        }
    
