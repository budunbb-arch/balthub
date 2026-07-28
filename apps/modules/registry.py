# /opt/balthub/apps/modules/registry.py

import importlib
import pkgutil

MODULE_HANDLERS = {}


def autodiscover_modules():
    """
    Ищет все файлы в apps.modules, содержащие:

        MODULE = "default/modules/xxx.html"

        def get_context(...):

    и регистрирует их обработчики.
    """

    from apps import modules

    MODULE_HANDLERS.clear()

    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):

        module = importlib.import_module(
            f"apps.modules.{module_name}"
        )

        template = getattr(module, "MODULE", None)
        handler = getattr(module, "get_context", None)

        if template and callable(handler):

            MODULE_HANDLERS[template] = handler