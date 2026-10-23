# apps/estates/parsing/cache.py

from apps.core.dictionaries.models import (
    Currency,
    DealType,
    PropertyType,
    PropertyCategory,
    FinishType,
    BalconyType,
    BathroomUnitType,
    HouseStructureType,
    BuildingStatus,
    City,
    District,
    ProjectType,
)
from apps.estates.developers.models import Developer
from apps.estates.projects.models import Project, ProjectDescription, ProjectParams
from apps.estates.houses.models import House, HouseParams
from apps.estates.flats.models import FlatDeal, FlatParams, Flat

from django.utils import timezone

from apps.estates.parsing.utils import cache_key

import re


class ImportCache:

    def __init__(self):
        self.dictionaries = {}
        self.project_types = []
        self.default_project_type = None

        self.cities = {}
        self.districts = {}

        self.developers = {}
        self.projects = {}
        self.houses = {}
        self.flats = {}
        self.project_descriptions = {}
        self.flat_deals = {}
        self.project_params = {}
        self.house_params = {}
        self.flat_params = {}

        self.currencies = {}


    def _resolve(self, cache, key, factory):

        obj = cache.get(key)

        if obj:
            # Если объект наследуется от BaseModel и был удалён — восстанавливаем
            if getattr(obj, "is_deleted", False):
                obj.restore()
                obj.refresh_from_db()
            return obj, False

        obj = factory()
        obj.save()

        cache[key] = obj

        return obj, True


    def load_dictionary(self, model):
        self.dictionaries[model] = {
            cache_key(obj.name): obj
            for obj in model.objects.all()
        }


    def load_dictionaries(self):
        for model in (
            Currency,
            DealType,
            PropertyType,
            PropertyCategory,
            FinishType,
            BalconyType,
            BathroomUnitType,
            HouseStructureType,
            BuildingStatus,
        ):
            self.load_dictionary(model)

    def load_project_types(self):
        self.project_types = list(ProjectType.objects.order_by("id"))
        default_project_types = [
            project_type
            for project_type in self.project_types
            if project_type.default is True
        ]
        if len(default_project_types) != 1:
            raise RuntimeError(
                "В справочнике типов проектов должен быть ровно один тип "
                "с default=True."
            )

        self.default_project_type = default_project_types[0]

    def resolve_project_type(self, project_name):
        if self.default_project_type is None:
            raise RuntimeError("Типы проектов не загружены.")
        if not project_name:
            raise RuntimeError("В объявлении отсутствует название проекта.")

        matches = []
        for project_type in self.project_types:
            for value in (project_type.name, project_type.project_type_alias):
                value = (value or "").strip()
                if not value:
                    continue
                pattern = rf"(?<!\w){re.escape(value)}(?!\w)"
                if re.search(pattern, project_name, re.IGNORECASE):
                    matches.append((len(value), project_type, value))

        if not matches:
            return project_name, self.default_project_type

        longest_match_length = max(length for length, _, _ in matches)
        longest_matches = [
            (project_type, value)
            for length, project_type, value in matches
            if length == longest_match_length
        ]
        matching_type_ids = {project_type.id for project_type, _ in longest_matches}
        if len(matching_type_ids) > 1:
            matched_values = ", ".join(
                sorted({value for _, value in longest_matches}, key=str.casefold)
            )
            raise RuntimeError(
                f"Неоднозначный тип для названия проекта {project_name!r}: "
                f"{matched_values}."
            )

        project_type, matched_value = longest_matches[0]
        clean_name = re.sub(
            rf"(?<!\w){re.escape(matched_value)}(?!\w)",
            "",
            project_name,
            flags=re.IGNORECASE,
        )
        clean_name = re.sub(r"\s+", " ", clean_name).strip(
            " \t\r\n-–—,.;:|«»\"'()[]"
        )
        if not clean_name:
            raise RuntimeError(
                f"Совпадение с типом проекта оставило пустое название: "
                f"{project_name!r}."
            )

        return clean_name, project_type
    

    def load_cities(self):

        self.cities = {
            cache_key(c.name): c
            for c in City.objects.all()
        }

    def load_districts(self):

        self.districts = {
            (
                d.city_id,
                cache_key(d.name),
            ): d
            for d in District.objects.only(
                "id",
                "city_id",
                "name",
            )
        }


    def load_developers(self):

        self.developers = {
            cache_key(d.name): d
            for d in Developer.objects.all().only("id", "name", "is_deleted")
        }


    def load_projects(self):

        self.projects = {
            cache_key(p.external_id): p
            for p in Project.objects.select_related("project_type").only(
                "id",
                "external_id",
                "developer_id",
                "is_deleted",
                "name",
                "project_type",
            )
        }


    def load_project_params(self):

        self.project_params = {
            cache_key(str(obj.project_id)): obj
            for obj in ProjectParams.objects.only(
                "id",
                "project_id",
                "city_id",
                "district_id",
                "property_type_id",
                "property_category_id",
            )
        }

    
    def load_project_descriptions(self):

        self.project_descriptions = {
            cache_key(str(pd.project_id)): pd
            for pd in ProjectDescription.objects.only(
                "id",
                "project_id",
                "hash",
                "description",
            )
        }


    def load_houses(self):

        self.houses = {
            cache_key(h.external_id): h
            for h in House.objects.all().only(
                "id",
                "external_id",
                "project_id",
                "is_deleted",
            )
        }


    def load_house_params(self):

        self.house_params = {
            cache_key(str(obj.house_id)): obj
            for obj in HouseParams.objects.only(
                "id",
                "house_id",
            )
        }


    def load_flats(self):

        self.flats = {
            cache_key(f.external_id): f
            for f in Flat.objects.all().only(
                "id",
                "external_id",
                "house_id",
                "number",
                "is_deleted",
            )
        }


    def load_flat_params(self):

        self.flat_params = {
            cache_key(str(obj.flat_id)): obj
            for obj in FlatParams.objects.only(
                "id",
                "flat_id",
            )
        }


    def load_flat_deals(self):

        self.flat_deals = {
            cache_key(str(f.flat_id)): f
            for f in FlatDeal.objects.only(
                "id",
                "flat_id",
                "deal_type_id",
                "price",
                "currency_id",
                "mortgage",
                "haggle",
            )
        }


    def load_currencies(self):

        self.currencies = {
            cache_key(c.code): c
            for c in Currency.objects.only(
                "id",
                "code",
            )
        }


    def extract_developer_name(self, description):

        if not description:
            return None

        patterns = (
            r"Застройщик:\s*(.+?)(?:\.\s|$)",
            r"Застройщик\s*-\s*(.+?)(?:\.\s|$)",
        )

        for pattern in patterns:
            m = re.search(pattern, description)
            if m:
                return m.group(1).strip().rstrip(".")

        return None


    def resolve_dictionary(self, model, value, mapping=None):

        if not value:
            return None

        value = value.strip()

        if mapping:
            value = mapping.get(cache_key(value), value)

        key = cache_key(value)

        cache = self.dictionaries.setdefault(model, {})

        obj, _ = self._resolve(
            cache=cache,
            key=key,
            factory=lambda: model(name=value),
        )

        return obj
    

    def resolve_finish_type(self, value):
        return self.resolve_dictionary(FinishType, value)

    def resolve_property_type(self, value):
        return self.resolve_dictionary(PropertyType, value)

    def resolve_property_category(self, value):
        return self.resolve_dictionary(PropertyCategory, value)

    def resolve_building_status(self, value, mapping=None):
        return self.resolve_dictionary(
            BuildingStatus,
            value,
            mapping,
        )

    def resolve_deal_type(self, value):
        return self.resolve_dictionary(
            DealType,
            value,
        )
    

    def resolve_city(self, value):

        if not value:
            return None

        value = value.strip().title()

        obj, _ = self._resolve(
            cache=self.cities,
            key=cache_key(value),
            factory=lambda: City(
                name=value,
            ),
        )

        return obj
    

    def resolve_district(self, city, name):

        if not city or not name:
            return None

        key = (
            city.id,
            cache_key(name),
        )

        obj, _ = self._resolve(
            cache=self.districts,
            key=key,
            factory=lambda: District(
                city=city,
                name=name.strip(),
            ),
        )

        return obj
    

    def resolve_developer(self, description):

        name = self.extract_developer_name(description)

        if not name:
            return None, False

        return self._resolve(
            cache=self.developers,
            key=cache_key(name),
            factory=lambda: Developer(
                name=name,
                is_public=True,
                published_at=timezone.now(),
            ),
        )

    def resolve_project(
        self,
        external_id,
        developer,
        name,
        meta_title,
        seo_h1,
    ):

        return self._resolve(
            cache=self.projects,
            key=cache_key(external_id),
            factory=lambda: Project(
                external_id=external_id,
                developer=developer,
                name=name,
                meta_title=meta_title,
                seo_h1=seo_h1,
                is_public=True,
                published_at=timezone.now(),
            ),
        )
    

    def resolve_project_params(self, project):

        return self._resolve(
            cache=self.project_params,
            key=cache_key(str(project.id)),
            factory=lambda: ProjectParams(
                project=project,
            ),
        )
    

    def resolve_project_description(
        self,
        project,
        description,
        description_hash,
    ):
        
        return self._resolve(
        cache=self.project_descriptions,
        key=cache_key(str(project.id)),
        factory=lambda: ProjectDescription(
            project=project,
            description=description,
            hash=description_hash,
        ),
    )


    def resolve_house(
        self,
        external_id,
        project,
    ):

        return self._resolve(
            cache=self.houses,
            key=cache_key(external_id),
            factory=lambda: House(
                external_id=external_id,
                project=project,
                is_public=True,
            ),
        )


    def resolve_house_params(self, house):

        return self._resolve(
            cache=self.house_params,
            key=cache_key(str(house.id)),
            factory=lambda: HouseParams(
                house=house,
            ),
        )


    def resolve_flat(
        self,
        external_id,
        house,
        number=None,
        plan=None,
    ):

        return self._resolve(
            cache=self.flats,
            key=cache_key(external_id),
            factory=lambda: Flat(
                external_id=external_id,
                house=house,
                number=number,
                plan=plan,
                is_public=True,
            ),
        )


    def resolve_flat_params(self, flat):

        return self._resolve(
            cache=self.flat_params,
            key=cache_key(str(flat.id)),
            factory=lambda: FlatParams(
                flat=flat,
            ),
        )
    

    def resolve_flat_deal(
        self,
        flat,
    ):
        
        return self._resolve(
            cache=self.flat_deals,
            key=cache_key(str(flat.id)),
            factory=lambda: FlatDeal(
                flat=flat,
            ),
        )


    def resolve_currency(self, code):

        if not code:
            return None

        code = code.strip().upper()
        
        obj, _ = self._resolve(
            cache=self.currencies,
            key=cache_key(code),
            factory=lambda: Currency(
                code=code,
                name=code,
            ),
        )

        return obj