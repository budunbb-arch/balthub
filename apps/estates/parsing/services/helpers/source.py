def apply_source(obj, parser):
    """
    Проставляет источник только при первом создании объекта.
    """

    if obj.source_id is None:
        obj.source = parser