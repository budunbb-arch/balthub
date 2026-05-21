import importlib
import pkgutil

MODULE_FUNCTIONS = []


def autodiscover_modules():
    from apps import modules

    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        module = importlib.import_module(f"apps.modules.{module_name}")

        for attr_name in dir(module):
            if attr_name.startswith("get_"):
                func = getattr(module, attr_name)

                if callable(func):
                   if func not in MODULE_FUNCTIONS: 
                       MODULE_FUNCTIONS.append(func)
