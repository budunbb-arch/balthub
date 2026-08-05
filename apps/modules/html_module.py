# /opt/balthub/apps/modules/html_module.py

MODULE = "default/modules/html_module.html"


def get_context(request, module):
    html_module = getattr(module, "html_module", None)

    return {
        "html_module": html_module,
        "html_content": getattr(html_module, "code", None),
    }
