# copied from cpython repo
# https://github.com/python/cpython/blob/7f97c8e367869e2aebe9f28bc5f8d4ce36448878/Lib/_collections_abc.py#L104-L114
def check_methods(C, *methods):
    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True
