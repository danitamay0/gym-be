from rebar import registry


@registry.handles(
    rule="/",
    method="GET",
)
def categories():
    """
    get categories
    """
    return {}
