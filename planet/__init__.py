import logging

from planet.__about__ import version as __version__

logging.getLogger("planet").addHandler(logging.NullHandler())
