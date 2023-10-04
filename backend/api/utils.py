def value_to_int(value):
    try:
        return int(value)
    except: # noqa
        return None
