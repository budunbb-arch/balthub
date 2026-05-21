class FilterField:
    pass


class FilterSet:
    def __init__(self, *args, **kwargs):
        pass

    def apply(self):
        raise NotImplementedError(
            "Old FilterSet removed. Use SearchEngine."
        )