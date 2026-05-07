import string

BASE62 = string.ascii_letters + string.digits

def encode_base62(num):
    if num == 0:
        return BASE62[0]

    base = len(BASE62)
    result = []

    while num:
        num, rem = divmod(num, base)
        result.append(BASE62[rem])

    return ''.join(reversed(result))