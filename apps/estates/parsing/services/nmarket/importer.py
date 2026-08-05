# /opt/balthub/apps/estates/parsing/services/importer.py

from lxml import etree
from django.utils import timezone

from apps.estates.parsing.utils import (
    extract_deadline,
    normalize_deadline,
    generate_hash,
    extract_project_description,
    normalize_text_block,
    to_bool,
)
from apps.estates.parsing.constants import BUILDING_STATUS_MAPPING
from apps.estates.developers.models import Developer
from apps.estates.projects.models import Project, ProjectImage
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat

from apps.core.dictionaries.models import (
    PropertyType,
    PropertyCategory,
    FinishType,
    BalconyType,
    BathroomUnitType,
    HouseStructureType,
    BuildingStatus,
)
from apps.estates.parsing.management.execution.parser_cancel import ParserCancelChecker


from apps.estates.parsing.utils import cache_key

from . import helpers
from . import images
from .images import normalize_image_url
from apps.estates.parsing.cache import ImportCache
from apps.estates.parsing.services.nmarket.helpers import BulkUpdater


import logging

logger = logging.getLogger(__name__)


class NMarketImporter:

    def __init__(self, feed_path, parser_run):
        self.feed_path = feed_path
        self.parser_run = parser_run
        self.bulk = BulkUpdater()

        self.cache = ImportCache()
        self.cache.load_dictionaries()
        self.cache.load_cities()
        self.cache.load_districts()
        self.cache.load_developers()
        self.cache.load_projects()
        self.cache.load_project_descriptions()
        self.cache.load_project_params()
        self.cache.load_houses()
        self.cache.load_house_params()
        self.cache.load_flats()
        self.cache.load_flat_deals()
        self.cache.load_flat_params()
        self.cache.load_currencies()

        # Сборник всех project_images для bulk-синхронизации после цикла
        self._project_images_by_project = {}
        # Сборник всех скачанных изображений для генерации variants после цикла
        self._downloaded_images = []


    def bulk_update(self, obj, **fields):
        changed = helpers.update_instance(obj, **fields)

        if changed:
            self.bulk.add(obj, changed)


    def save_or_bulk(
        self,
        instance,
        created,
        stats,
        created_key,
        updated_key,
        **fields,
    ):

        if created:
            helpers.update_instance(instance, **fields)
            instance.ensure_slug()
            instance.save()
            stats[created_key] += 1
            return []

        changed = helpers.update_instance(instance, **fields)

        if changed:
            self.bulk.add(instance, changed)
            stats[updated_key] += 1

        return changed


    def _collect_images(self, offer, ns):
        """Собрать все URL изображений из offer'а, нормализовать."""
        offer_images = offer.findall("y:image", ns)

        flat_plan = None
        house_image = None
        house_plan = None
        project_images = []

        for img in offer_images:
            raw_url = img.text.strip() if img.text else None
            tag = img.get("tag")

            if not raw_url:
                continue

            # Единая нормализация: убрать пробелы, добавить https: если без схемы
            url = raw_url.strip()
            if url.startswith("//"):
                url = "https:" + url

            if tag == "plan":
                flat_plan = url
            elif tag == "housemain":
                house_image = url
            elif tag == "floorplan":
                house_plan = url
            else:
                project_images.append(url)

        return flat_plan, house_image, house_plan, project_images


    def _parse_offer_data(self, offer, ns):
        """Парсит XML offer один раз и возвращает dict со всеми данными."""
        description = helpers.get_text(offer, "y:description", ns)
        return {
            "description": description,
            "external_id": offer.get("internal-id"),
            "property_type": helpers.get_text(offer, "y:property-type", ns),
            "category": helpers.get_text(offer, "y:category", ns),
            "building_name": helpers.get_text(offer, "y:building-name", ns),
            "complex_id": helpers.get_text(offer, "y:nmarket-complex-id", ns),
            "building_id": helpers.get_text(offer, "y:nmarket-building-id", ns),
            "building_section": helpers.get_text(offer, "y:building-section", ns),
            "building_phase": helpers.get_text(offer, "y:building-phase", ns),
            "building_type": helpers.get_text(offer, "y:building-type", ns),
            "building_state": helpers.get_text(offer, "y:building-state", ns),
            "built_year": helpers.get_text(offer, "y:built-year", ns),
            "floors_total": helpers.get_text(offer, "y:floors-total", ns),
            "lift": helpers.get_text(offer, "y:lift", ns),
            "parking": helpers.get_text(offer, "y:parking", ns),
            "rooms": helpers.get_text(offer, "y:rooms", ns),
            "floor": helpers.get_text(offer, "y:floor", ns),
            "renovation": helpers.get_text(offer, "y:renovation", ns),
            "balcony": helpers.get_text(offer, "y:balcony", ns),
            "bathroom_unit": helpers.get_text(offer, "y:bathroom-unit", ns),
            "ceiling_height": helpers.get_text(offer, "y:ceiling-height", ns),
            "type": helpers.get_text(offer, "y:type", ns),
            "mortgage": helpers.get_text(offer, "y:mortgage", ns),
            "haggle": helpers.get_text(offer, "y:haggle", ns),
            "locality_name": helpers.get_nested_text(offer, "y:location/y:locality-name", ns),
            "district": helpers.get_nested_text(offer, "y:location/y:district", ns),
            "address": helpers.get_nested_text(offer, "y:location/y:address", ns),
            "apartment": helpers.get_nested_text(offer, "y:location/y:apartment", ns),
            "latitude": helpers.get_nested_text(offer, "y:location/y:latitude", ns),
            "longitude": helpers.get_nested_text(offer, "y:location/y:longitude", ns),
            "price_value": helpers.get_nested_text(offer, "y:price/y:value", ns),
            "price_currency": helpers.get_nested_text(offer, "y:price/y:currency", ns) or "RUR",
            "area_value": helpers.get_nested_text(offer, "y:area/y:value", ns),
            "living_space_value": helpers.get_nested_text(offer, "y:living-space/y:value", ns),
            "kitchen_space_value": helpers.get_nested_text(offer, "y:kitchen-space/y:value", ns),
        }


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

        xml_parser = etree.XMLParser(recover=True)
        tree = etree.parse(str(self.feed_path), xml_parser)
        root = tree.getroot()

        ns = {"y": "http://webmaster.yandex.ru/schemas/feed/realty/2010-06"}

        # --- Шаг 1: Собрать все URL изображений и скачать их пакетно ---
        logger.info("Collecting image URLs from feed...")

        all_images_to_download = {
            "flat_plans": [],
            "houses": [],
            "house_plans": [],
            "project_images": [],
        }

        for offer in root.findall("y:offer", ns):
            flat_plan, house_image, house_plan, proj_imgs = self._collect_images(offer, ns)
            if flat_plan:
                all_images_to_download["flat_plans"].append(flat_plan)
            if house_image:
                all_images_to_download["houses"].append(house_image)
            if house_plan:
                all_images_to_download["house_plans"].append(house_plan)
            for url in proj_imgs:
                all_images_to_download["project_images"].append(url)

        logger.info(
            "Images to download: flat_plans=%d, houses=%d, house_plans=%d, projects=%d",
            len(all_images_to_download["flat_plans"]),
            len(all_images_to_download["houses"]),
            len(all_images_to_download["house_plans"]),
            len(all_images_to_download["project_images"]),
        )

        # Параллельная загрузка всех изображений
        downloaded = {}
        for subfolder, urls in all_images_to_download.items():
            if urls:
                logger.info("Downloading %s images (%d)...", subfolder, len(urls))
                downloaded[subfolder] = images.download_images(urls, subfolder)
                logger.info("Downloaded %d %s images", len(downloaded[subfolder]), subfolder)
                if downloaded[subfolder]:
                    sample_key = next(iter(downloaded[subfolder]))
                    logger.info("  sample key  : %s", sample_key)
                    logger.info("  sample value: %s", downloaded[subfolder][sample_key])
            else:
                downloaded[subfolder] = {}

        # --- Шаг 2: Основной цикл импорта ---
        for offer in root.findall("y:offer", ns):

            processed += 1

            data = self._parse_offer_data(offer, ns)

            # ------------------------
            # IMAGES — используем уже скачанные
            # ------------------------
            flat_plan, house_image, house_plan, proj_imgs = self._collect_images(offer, ns)

            orig_flat = flat_plan
            orig_house = house_image

            flat_plan = helpers.pick_downloaded(flat_plan, downloaded["flat_plans"])
            house_image = helpers.pick_downloaded(house_image, downloaded["houses"])
            house_plan = helpers.pick_downloaded(house_plan, downloaded["house_plans"])
            project_images = helpers.pick_downloaded_list(proj_imgs, downloaded["project_images"])

            # отладка: проверить первые несколько offer'ов
            if processed <= 3:
                logger.info("  [DEBUG flat_plan]  orig=%s | downloaded=%s", orig_flat, flat_plan)
                logger.info("  [DEBUG house_image] orig=%s | downloaded=%s", orig_house, house_image)
                logger.info("  [DEBUG project_imgs] count=%d -> %d", len(proj_imgs), len(project_images))
                if proj_imgs and downloaded["project_images"]:
                    logger.info("    first proj orig=%s | in map=%s", proj_imgs[0], proj_imgs[0] in downloaded["project_images"])

            # Запомним project_images для bulk-синхронизации после цикла
            if project_images:
                incoming_set = set(filter(None, project_images))
                # Отложим синхронизацию — будем использовать project_id как ключ
                # (project ещё может не существовать, запомним external_id комплекса)
                self._project_images_by_project[data["complex_id"]] = incoming_set

            # ------------------------
            # DEVELOPER
            # ------------------------
            developer, created = self.cache.resolve_developer(data["description"])

            if developer is None:
                continue

            self.save_or_bulk(
                developer,
                created,
                stats,
                "developers_created",
                "developers_updated",
                origin_type="parser",
                origin_parser=source_parser,
                is_public=True,
                published_at=developer.published_at or timezone.now(),
            )

            # ------------------------
            # PROJECT
            # ------------------------
            project, created = self.cache.resolve_project(
                external_id=data["complex_id"],
                developer=developer,
                name=data["building_name"],
            )

            if developer is not None:
                self.save_or_bulk(
                    project,
                    created,
                    stats,
                    "projects_created",
                    "projects_updated",
                    origin_type="parser",
                    origin_parser=source_parser,
                    is_public=True,
                    published_at=project.published_at or timezone.now(),
                    developer=developer,
                )


            # ------------------------
            # PROJECT DESCRIPTION
            # ------------------------

            project_description = extract_project_description(data["description"])

            if project_description:

                project_description = normalize_text_block(project_description)
                description_hash = generate_hash(project_description)

                project_description_obj, _ = self.cache.resolve_project_description(
                    project,
                    project_description,
                    description_hash,
                )

                if project_description_obj is not None:
                    self.bulk_update(
                        project_description_obj,
                        description=project_description,
                        hash=description_hash,
                    )


            # PROJECT PARAMS
            city = self.cache.resolve_city(data["locality_name"])

            district = self.cache.resolve_district(
                city,
                data["district"],
            ) if city else None

            project_params, _ = self.cache.resolve_project_params(project)

            if project_params is not None:
                self.bulk_update(
                    project_params,
                    city=city,
                    district=district,
                    property_type=self.cache.resolve_dictionary(PropertyType, data["property_type"]),
                    property_category=self.cache.resolve_dictionary(PropertyCategory, data["category"]),
                )

            # ------------------------
            # HOUSE
            # ------------------------
            external_id = data["building_id"]

            house, created = self.cache.resolve_house(
                external_id,
                project,
            )

            if project is not None:
                self.save_or_bulk(
                    house,
                    created,
                    stats,
                    "houses_created",
                    "houses_updated",
                    origin_type="parser",
                    origin_parser=source_parser,
                    project=project,
                    image=house_image,
                    plan=house_plan,
                    is_public=True,
                )

            # HOUSE PARAMS
            deadline_raw = extract_deadline(data["description"])
            deadline = normalize_deadline(deadline_raw)

            house_params, _ = self.cache.resolve_house_params(house)

            if house_params is not None:
                self.bulk_update(
                    house_params,
                    address=data["address"],
                    corpus=data["building_section"],
                    phase=data["building_phase"],
                    deadline=deadline,
                    deadline_year=helpers.to_int(data["built_year"]),
                    floors=helpers.to_int(data["floors_total"]),
                    house_structure_type=self.cache.resolve_dictionary(HouseStructureType, data["building_type"]),
                    building_status=self.cache.resolve_dictionary(BuildingStatus, data["building_state"], mapping=BUILDING_STATUS_MAPPING),
                    lift=to_bool(data["lift"]),
                    parking=to_bool(data["parking"]),
                    latitude=helpers.to_float(data["latitude"]),
                    longitude=helpers.to_float(data["longitude"]),
                )

            # ------------------------
            # FLAT
            # ------------------------
            apartment = data["apartment"]

            flat, created = self.cache.resolve_flat(
                external_id=data["external_id"],
                house=house,
                number=apartment.strip() if apartment else None,
                plan=flat_plan,
            )

            if house is not None:
                self.save_or_bulk(
                    flat,
                    created,
                    stats,
                    "flats_created",
                    "flats_updated",
                    origin_type="parser",
                    origin_parser=source_parser,
                    house=house,
                    number=apartment.strip() if apartment else None,
                    plan=flat_plan,
                    is_public=True,
                    published_at=flat.published_at or timezone.now()
                )

            flat_params, _ = self.cache.resolve_flat_params(flat)

            rooms_value = helpers.to_int(data["rooms"])
            if rooms_value is not None:
                rooms_alias = (
                    "Студия" if rooms_value == 0
                    else f"{rooms_value}-комнатная"
                )
            else:
                rooms_alias = None

            if flat_params is not None:
                self.bulk_update(
                    flat_params,
                    rooms=rooms_value,
                    rooms_alias=rooms_alias,
                    square=helpers.to_float(data["area_value"]),
                    floor=helpers.to_int(data["floor"]),
                    finish_type=self.cache.resolve_dictionary(FinishType, data["renovation"]),
                    balcony_type=self.cache.resolve_dictionary(BalconyType, data["balcony"]),
                    bathroom_unit_type=self.cache.resolve_dictionary(BathroomUnitType, data["bathroom_unit"]),
                    living_square=helpers.to_float(data["living_space_value"]),
                    kitchen_square=helpers.to_float(data["kitchen_space_value"]),
                    ceiling_height=helpers.to_float(data["ceiling_height"]),
                )

            # ------------------------
            # FLAT DEAL
            # ------------------------

            price_value = helpers.to_float(data["price_value"])

            currency_code = data["price_currency"] or "RUR"
            currency = self.cache.resolve_currency(currency_code)

            deal_type_obj = self.cache.resolve_deal_type(data["type"])

            deal, _ = self.cache.resolve_flat_deal(flat)

            if deal is not None:
                self.bulk_update(
                    deal,
                    deal_type=deal_type_obj,
                    price=price_value,
                    currency=currency,
                    mortgage=(
                        data["mortgage"].lower() == "true"
                        if data["mortgage"] else False
                    ),
                    haggle=(
                        data["haggle"].lower() == "true"
                        if data["haggle"] else False
                    ),
                )

            logger.info(
                "Flat %s imported (deal: %s)",
                flat.external_id,
                deal_type_obj,
            )

            stats["offers"] += 1


        # --- Шаг 3: Bulk update ---
        self.bulk.flush()

        # --- Шаг 4: Bulk-синхронизация ProjectImage ---
        logger.info("Syncing project images...")
        self._sync_project_images_bulk()
        logger.info("Project images synced.")

        # --- Шаг 5: Генерация image variants после цикла ---
        logger.info("Generating image variants...")
        images.generate_all_variants()
        logger.info("Image variants generated.")

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


    def _sync_project_images_bulk(self):
        """Bulk-синхронизация ProjectImage после основного цикла."""
        projects_to_sync = {}  # project_id -> set of image URLs

        # Сопоставляем external_id (complex_id) с project через кэш
        for complex_id, image_set in self._project_images_by_project.items():
            project = self.cache.projects.get(cache_key(complex_id))
            if project:
                projects_to_sync[project.id] = image_set

        if not projects_to_sync:
            return

        # Получить существующие связи
        existing_qs = ProjectImage.objects.filter(
            project_id__in=projects_to_sync.keys()
        ).values("project_id", "image")

        existing_by_project = {}
        for row in existing_qs:
            existing_by_project.setdefault(row["project_id"], set()).add(row["image"])

        # Собрать, что нужно удалить и что добавить
        to_delete_ids = []
        to_create = []

        for project_id, incoming_images in projects_to_sync.items():
            existing = existing_by_project.get(project_id, set())

            to_remove = existing - incoming_images
            if to_remove:
                to_delete_ids.extend(
                    ProjectImage.objects.filter(
                        project_id=project_id,
                        image__in=to_remove,
                    ).values_list("id", flat=True)
                )

            to_add = incoming_images - existing
            for image_url in to_add:
                to_create.append(ProjectImage(project_id=project_id, image=image_url))

        # Выполнить bulk-операции
        if to_delete_ids:
            ProjectImage.objects.filter(id__in=to_delete_ids).delete()

        if to_create:
            ProjectImage.objects.bulk_create(to_create, batch_size=500, ignore_conflicts=True)