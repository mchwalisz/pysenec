def parse(value):
    """Parses numeric values, Senec supplies them as hex.
    """
    key, value = value.split("_")
    if key == "u8":
        return int(value, 16)
