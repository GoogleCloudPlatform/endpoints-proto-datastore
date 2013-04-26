# Copyright 2013 Google Inc. All Rights Reserved.

"""Utility module for tests.

NOTE: The which method below is borrowed from a project with a different
LICENSE. See README.md for this project for more details.
"""


import os


PATH_ENV_VAR = 'PATH'
# Used by Windows to add potential extensions to scripts on path
PATH_EXTENSIONS_ENV_VAR = 'PATHEXT'


def which(name, flags=os.X_OK):
    """Search PATH for executable files with the given name.

    On newer versions of MS-Windows, the PATHEXT environment variable will be
    set to the list of file extensions for files considered executable. This
    will normally include things like ".EXE". This fuction will also find files
    with the given name ending with any of these extensions.

    On MS-Windows the only flag that has any meaning is os.F_OK. Any other
    flags will be ignored.

    NOTE: Adapted from the Twisted project:
    ('https://twistedmatrix.com/trac/browser/tags/releases/twisted-8.2.0/'
     'twisted/python/procutils.py')

    Args:
      name: String; the name for which to search.
      flags: Integer; arguments to os.access.

    Returns:
      String containing the full path of the named file combined with one
        of the directory choices on PATH (optionally with an extension added).
        If the script is not on the path, None is returned.
    """
    result = []

    path_extension = os.getenv(PATH_EXTENSIONS_ENV_VAR, '')
    valid_extensions = [extension
                        for extension in path_extension.split(os.pathsep)
                        if extension]

    path = os.getenv(PATH_ENV_VAR)
    if path is None:
        return

    for directory_on_path in path.split(os.pathsep):
        potential_match = os.path.join(directory_on_path, name)

        # Unix
        if os.access(potential_match, flags):
            return potential_match

        # Windows helper
        for extension in valid_extensions:
            potential_match_with_ext = potential_match + extension
            if os.access(potential_match_with_ext, flags):
                return potential_match_with_ext

    return result
