import pkgutil
import sys

import pluggy

hookspec = pluggy.HookspecMarker("PyAria2ng")
hookimpl = pluggy.HookimplMarker("PyAria2ng")


class UrlProviderBackend(object):
    """A hook specification namespace.
    """

    @hookspec
    def get_urls(self, uri):
        """Return URLs for download
        """


registry = pluggy.PluginManager("PyAria2ng")
registry.add_hookspecs(UrlProviderBackend)
extensions = []


def load_builtin_plugins(dirname):
    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            try:
                ext = importer.find_module(package_name).load_module(package_name)
                extension_class = getattr(ext, "Extension")
                extension_class.setup()
                extensions.append(extension_class)
            except Exception as er:
                print(er)
