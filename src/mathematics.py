
def vector2D_add(a : tuple,b : tuple):
    return tuple(map(sum, zip(a, b)))


def vector2D_sub(a: tuple, b : tuple):
    """
    Subtract b from a element-wise.
    """
    neg_b = vector2D_scalar_multiply(b, -1)
    return vector2D_add(a,neg_b)

def vector2D_scalar_multiply(tpl : tuple, scalar : float):
    return tuple(map(lambda x : x * scalar, tpl))