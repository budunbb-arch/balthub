# /opt/balthub/apps/modules/registry.py

import importlib
import pkgutil
import logging

MODULE_HANDLERS = {}

logger = logging.getLogger(__name__)


def autodiscover_modules():
    """
    Ищет все файлы в apps.modules, содержащие:

        MODULE = "default/modules/xxx.html"

        def get_context(...):

    и регистрирует их обработчики.
    """

    from apps import modules

    MODULE_HANDLERS.clear()

    logger.info("[MODULE REGISTRY] starting autodiscover")

    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):

        module = importlib.import_module(
            f"apps.modules.{module_name}"
        )

        template = getattr(module, "MODULE", None)
        handler = getattr(module, "get_context", None)

        if template and callable(handler):
            MODULE_HANDLERS[template] = handler
            logger.info("[MODULE REGISTRY] registered core %s -> %s", template, module_name)

    # Also scan apps.leads for module handlers
    try:
        from apps import leads
        for _, module_name, _ in pkgutil.iter_modules(leads.__path__):
            module = importlib.import_module(
                f"apps.leads.{module_name}"
            )
            template = getattr(module, "MODULE", None)
            handler = getattr(module, "get_context", None)
            if template and callable(handler):
                MODULE_HANDLERS[template] = handler
                logger.info("[MODULE REGISTRY] registered leads %s -> %s", template, module_name)
    except Exception:
        logger.exception("[MODULE REGISTRY] leads scan failed")