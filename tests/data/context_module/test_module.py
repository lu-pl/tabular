"""Module for testing TaCL's --module-context flag."""

import functools

from itertools import count


some_variable = "Have more fun!"


@functools.wraps(count)
def _counter(*args, **kwargs):
    """Simple itertools count factory."""

    _count = count(*args, **kwargs)

    def _inner():
        return next(_count)

    return _inner


counter = _counter()
