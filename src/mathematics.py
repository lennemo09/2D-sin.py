
def tuple_add(a : tuple,b : tuple):
    return tuple(map(sum, zip(a, b)))


def tuple_scalar_multiply(tpl : tuple, scalar : float):
    return tuple(map(lambda x : x * scalar, tpl))