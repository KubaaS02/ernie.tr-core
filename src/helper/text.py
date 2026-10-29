import unicodedata


def is_blank(value: str) -> bool:
    """
    Sprawdza, czy tekst jest pusty albo składa się wyłącznie z niewidocznych znaków.

    Za niewidoczne uznawane są wszystkie białe znaki Unicode oraz znaki formatujące
    z kategorii Unicode "Cf" (np. spacja zerowej szerokości U+200B),
    których nie usuwa str.strip ().

    Args:
        value: Tekst do sprawdzenia

    Returns:
        True, gdy po usunięciu znaków niewidocznych nie zostaje żaden znak,
        w przeciwnym razie False

    Examples:
        >>> is_blank ("")
        True
        >>> is_blank ("   ")
        True
        >>> is_blank ("\\u200b")
        True
        >>> is_blank (" a ")
        False
    """
    visible = "".join(t for t in value if unicodedata.category(t) != "Cf")
    return visible.strip() == ""
