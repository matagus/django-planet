from django.utils.module_loading import import_string

from planet.settings import PLANET_CONFIG


def get_post_filter_backend():
    backend_path = PLANET_CONFIG["POST_FILTER_BACKEND"]
    backend_cls = import_string(backend_path)
    return backend_cls()
