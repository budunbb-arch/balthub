# apps/core/cache_keys.py

def project_list_key(*args, **kwargs):
    return "projects_list"


def project_detail_key(project_id):
    return f"project_detail:{project_id}"


def house_list_key(*args, **kwargs):
    return "house_list"


def houses_project_key(project_id):
    return f"houses_project:{project_id}"


def house_flats_key(house_id):
    return f"house_flats:{house_id}"


def project_list_key(*args, **kwargs):
    return "projects_list"


def project_detail_key(project_id):
    return f"project_detail:{project_id}"