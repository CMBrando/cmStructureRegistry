from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class CMStructureRegistryMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Structure Registry"),
            "fas fa-building fa-fw",
            "cmStructureRegistry:index"
        )

    def render(self, request):
        if request.user.has_perm("cmStructureRegistry.view_structureregistry"):
            return MenuItemHook.render(self, request)
        return ""

class CMTimerMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Timers"),
            "fas fa-clock fa-fw",
            "cmStructureRegistry:timers"
        )

    def render(self, request):
        if request.user.has_perm("cmStructureRegistry.view_corptimer"):
            return MenuItemHook.render(self, request)
        return ""          


@hooks.register("menu_item_hook")
def register_menu():
    return CMTimerMenuItem()

@hooks.register("menu_item_hook")
def register_menu():
    return CMStructureRegistryMenuItem()    


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "cmStructureRegistry", r"^cmStructureRegistry/")
