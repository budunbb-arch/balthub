# /opt/balthub/apps/estates/parsing/management/commands/import_xml.py

from lxml import etree
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
import hashlib
import mimetypes
from PIL import Image, ImageOps

from django.conf import settings
from django.core.management.base import BaseCommand
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
    City,
    District,
    DealType,
    Currency,
)


class Command(BaseCommand):
    help = "Import XML feed"

    IMAGE_VARIANTS = {
        "flat_plans": [
            (480, None),
        ],
        "house_plans": [
            (800, 600),
            (200, 150),
        ],
        "houses": [
            (480, 640),
            (800, 600),
        ],
        "project_images": [
            (480, 640),
            (800, 600),
            (1200, 600),
            (200, 150),
        ],
    }

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, default="test.xml")

    def handle(self, *args, **kwargs):
        feed_path = Path(settings.FEEDS_DIR) / kwargs["file"]

        parser = etree.XMLParser(recover=True)
        tree = etree.parse(str(feed_path), parser)
        root = tree.getroot()

        ns = {"y": "http://webmaster.yandex.ru/schemas/feed/realty/2010-06"}

        for offer in root.findall("y:offer", ns):

            description = self.get_text(offer, "y:description", ns)

            # ------------------------
            # IMAGES PARSING (СНАЧАЛА!)
            # ------------------------
            images = offer.findall("y:image", ns)

            flat_plan = None
            house_image = None
            house_plan = None
            project_images = []

            for img in images:
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
            flat_plan = self.download_image(flat_plan, "flat_plans") or flat_plan
            house_image = self.download_image(house_image, "houses") or house_image
            house_plan = self.download_image(house_plan, "house_plans") or house_plan

            # убрать дубли URL из фида
            project_images = list(dict.fromkeys(project_images))

            # скачать изображения
            project_images = [
                self.download_image(url, "project_images") or url
                for url in project_images
            ]

            # убрать дубли после скачивания
            project_images = list(dict.fromkeys(project_images))

            # ------------------------
            # DEVELOPER
            # ------------------------
            developer = parse_and_resolve(
                Developer,
                description,
                patterns=[
                    r"Застройщик:\s*(.+?)(?:\.\s|$)",
                    r"Застройщик\s*-\s*(.+?)(?:\.\s|$)",
                ],
                normalize_rules=[]
            )

            # ------------------------
            # PROJECT
            # ------------------------
            project, _ = Project.objects.get_or_create(
                external_id=self.get_text(offer, "y:nmarket-complex-id", ns),
                defaults={
                    "name": self.get_text(offer, "y:building-name", ns),
                    "developer": developer,
                    "is_public": True,
                    "published_at": timezone.now(),
                }
            )

            updated_fields = []

            if not project.is_public:
                project.is_public = True
                updated_fields.append("is_public")

            if not project.published_at:
                project.published_at = timezone.now()
                updated_fields.append("published_at")

            if developer and project.developer != developer:
                project.developer = developer
                updated_fields.append("developer")

            if updated_fields:
                project.save(update_fields=updated_fields)


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
                self.get_nested_text(offer, "y:location/y:locality-name", ns)
            )

            district = resolve_district(
                city,
                self.get_nested_text(offer, "y:location/y:district", ns),
            ) if city else None

            project_params, _ = ProjectParams.objects.update_or_create(
                project=project,
                defaults={
                    "city": city,
                    "district": district,
                    "property_type": resolve_dictionary(
                        PropertyType,
                        self.get_text(offer, "y:property-type", ns)
                    ),
                    "property_category": resolve_dictionary(
                        PropertyCategory,
                        self.get_text(offer, "y:category", ns)
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
            external_id=self.get_text(offer, "y:nmarket-building-id", ns)

            house, created = House.objects.get_or_create(
                external_id=external_id,
                defaults={"project": project}
            )

            if not created and house.project != project:
                house.project = project
                house.save(update_fields=["project"])

            update_fields = []

            if house_image and house.image != house_image:
                house.image = house_image
                update_fields.append("image")

            if house_plan and house.plan != house_plan:
                house.plan = house_plan
                update_fields.append("plan")

            if update_fields:
                house.save(update_fields=update_fields)

            # HOUSE PARAMS
            deadline_raw = extract_deadline(description)
            deadline = normalize_deadline(deadline_raw)

            HouseParams.objects.update_or_create(
                house=house,
                defaults={
                    "address": self.get_nested_text(offer, "y:location/y:address", ns),
                    "corpus": self.get_text(offer, "y:building-section", ns),
                    "phase": self.get_text(offer, "y:building-phase", ns),
                    "deadline": deadline,

                    "deadline_year": self.to_int(
                        self.get_text(offer, "y:built-year", ns)
                    ),

                    "floors": self.to_int(self.get_text(offer, "y:floors-total", ns)),
                    "house_structure_type": resolve_dictionary(
                        HouseStructureType,
                        self.get_text(offer, "y:building-type", ns)
                    ),
                    "building_status": resolve_dictionary(
                        BuildingStatus,
                        self.get_text(offer, "y:building-state", ns),
                        mapping=BUILDING_STATUS_MAPPING
                    ),

                    "lift": to_bool(self.get_text(offer, "y:lift", ns)),
                    "parking": to_bool(self.get_text(offer, "y:parking", ns)),

                    "latitude": self.to_float(
                        self.get_nested_text(offer, "y:location/y:latitude", ns)
                    ),
                    "longitude": self.to_float(
                        self.get_nested_text(offer, "y:location/y:longitude", ns)
                    ),
                }
            )

            # ------------------------
            # FLAT
            # ------------------------
            apartment = self.get_nested_text(offer, "y:location/y:apartment", ns)

            flat, _ = Flat.objects.update_or_create(
                external_id=offer.get("internal-id"),
                defaults={
                    "house": house,
                    "number": apartment.strip() if apartment else None,
                    "plan": flat_plan
                }
            )

            FlatParams.objects.update_or_create(
                flat=flat,
                defaults={
                    "rooms": self.to_int(self.get_text(offer, "y:rooms", ns)),
                    "rooms_alias": f"{self.get_text(offer, 'y:rooms', ns)}к",
                    "square": self.to_float(
                        self.get_nested_text(offer, "y:area/y:value", ns)
                    ),
                    "floor": self.to_int(self.get_text(offer, "y:floor", ns)),
                    
                    "finish_type": resolve_dictionary(
                        FinishType,
                        self.get_text(offer, "y:renovation", ns)
                    ),
                    "balcony_type": resolve_dictionary(
                        BalconyType,
                        self.get_text(offer, "y:balcony", ns)
                    ),
                    "bathroom_unit_type": resolve_dictionary(
                        BathroomUnitType,
                        self.get_text(offer, "y:bathroom-unit", ns)
                    ),
                    "living_square": self.to_float(
                        self.get_nested_text(offer, "y:living-space/y:value", ns)
                    ),
                    "kitchen_square": self.to_float(
                        self.get_nested_text(offer, "y:kitchen-space/y:value", ns)
                    ),
                    "ceiling_height": self.to_float(
                        self.get_text(offer, "y:ceiling-height", ns)
                    ),
                }
            )

            # ------------------------
            # FLAT DEAL
            # ------------------------
            price_value = self.to_float(
                self.get_nested_text(offer, "y:price/y:value", ns)
            )

            currency_code = self.get_nested_text(offer, "y:price/y:currency", ns) or "RUR"
            currency = Currency.objects.filter(code__iexact=currency_code).first()

            deal_type_obj = resolve_dictionary(
                DealType,
                self.get_text(offer, "y:type", ns)
            )

            mortgage_value = self.get_text(offer, "y:mortgage", ns)
            haggle_value = self.get_text(offer, "y:haggle", ns)

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

            self.stdout.write(f"✔ Flat {flat.external_id} + deal {deal_type_obj}")

            

    # ------------------------
    # HELPERS
    # ------------------------

    def get_text(self, parent, path, ns):
        el = parent.find(path, ns)
        return el.text.strip() if el is not None and el.text else None

    def get_nested_text(self, parent, path, ns):
        el = parent.find(path, ns)
        return el.text.strip() if el is not None and el.text else None

    def to_int(self, value):
        try:
            return int(value)
        except:
            return None

    def to_float(self, value):
        try:
            return float(value)
        except:
            return None

    def download_image(self, url, subfolder):
        if not url:
            return None

        normalized_url = url.strip()
        if normalized_url.startswith("//"):
            normalized_url = "https:" + normalized_url
        if not normalized_url.lower().startswith(("http://", "https://")):
            return None

        media_root = Path(settings.MEDIA_ROOT)
        target_dir = media_root / "imported_images" / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            request = Request(normalized_url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=20) as response:
                if getattr(response, "status", 200) != 200:
                    return None

                content = response.read()
                if not content:
                    return None

                parsed = urlparse(normalized_url)
                basename = Path(unquote(parsed.path)).name
                ext = Path(basename).suffix.lower()
                if not ext or len(ext) > 5:
                    content_type = response.headers.get("Content-Type", "")
                    ext = mimetypes.guess_extension(content_type.split(";")[0].strip() or "") or ".jpg"

                file_hash = hashlib.md5(content).hexdigest()
                filename = f"{file_hash}{ext}"
                target_path = target_dir / filename

                if not target_path.exists():
                    target_path.write_bytes(content)

                self.generate_image_variants(target_path, subfolder)

                return f"{settings.MEDIA_URL.rstrip('/')}/{Path('imported_images') / subfolder / filename}"
        except Exception as exc:
            self.stderr.write(f"Failed to download image {normalized_url}: {exc}")
            return None

    def generate_image_variants(self, original_path, subfolder):
        """Создаёт копии изображений разных размеров и кэширует их на диске."""
        variants = self.IMAGE_VARIANTS.get(subfolder, [])

        for width, height in variants:
            self.save_image_variant(original_path, width, height)

    def save_image_variant(self, original_path, width, height=None):
        """Сохраняет одну уменьшенную версию изображения."""
        try:
            image = Image.open(original_path)
            image = ImageOps.exif_transpose(image)
            image_format = image.format or "JPEG"

            if height is None:
                max_size = (width, 10000)
                image.thumbnail(max_size, Image.LANCZOS)
            else:
                image = ImageOps.fit(
                    image,
                    (width, height),
                    Image.LANCZOS
                )

            if image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            base_name = original_path.stem
            ext = original_path.suffix.lower() or ".jpg"
            if height is None:
                size_suffix = f"{width}xauto"
            else:
                size_suffix = f"crop_{width}x{height}"
            variant_path = original_path.with_name(f"{base_name}_{size_suffix}{ext}")

            if variant_path.exists():
                return

            image.save(
                variant_path,
                format=image_format,
                quality=100,
                optimize=True,
            )
        except Exception as exc:
            self.stderr.write(f"Failed to create image variant for {original_path}: {exc}")

    def save_image_crop_variant(self, original_path, width):
        target_height = int(width * 4 / 3)

        with Image.open(original_path) as image:
            image = ImageOps.exif_transpose(image)
            cropped = ImageOps.fit(
                image,
                (width, target_height),
                Image.LANCZOS,
                centering=(0.5, 0.5)
            )

            if cropped.mode in ("RGBA", "LA"):
                background = Image.new("RGB", cropped.size, (255, 255, 255))
                background.paste(cropped, mask=cropped.split()[3])
                cropped = background
            elif cropped.mode != "RGB":
                cropped = cropped.convert("RGB")

            base = original_path.stem
            ext = original_path.suffix.lower() or ".jpg"
            variant_path = original_path.with_name(f"{base}_crop_{width}x{target_height}{ext}")

            if not variant_path.exists():
                cropped.save(variant_path, quality=85, optimize=True)