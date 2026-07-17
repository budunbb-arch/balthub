# /opt/balthub/apps/estates/parsing/services/registry.py

from apps.estates.parsing.services.nmarket.importer import NMarketImporter

IMPORTERS = {
    "nmarket": NMarketImporter,
}


def get_importer(engine):
    try:
        return IMPORTERS[engine]
    except KeyError:
        raise ValueError(f"Unknown parser engine: {engine}")