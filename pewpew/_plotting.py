# -*- coding: utf-8 -*-

import sys


def init_matplotlib(backend=None, debug=False):
    """Initialize the Matplotlib backend

    In some Mac distros, python is not installed as a framework.
    This means that using the TkAgg backend is the best solution
    (so it doesn't try to use the mac OS backend by default).

    Parameters
    ----------
    backend : str, optional
        The backend to default to
    """
    import matplotlib

    existing_backend = matplotlib.get_backend()
    if backend is not None:
        matplotlib.use(backend)

        if debug:
            sys.stderr.write(
                f"Currently using '{existing_backend}' matplotlib backend, "
                f"switching to '{backend}' backend\n"
            )
    elif debug:
        sys.stderr.write(f"Using '{existing_backend}' MPL backend\n")
