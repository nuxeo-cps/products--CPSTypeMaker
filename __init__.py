
from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory('skins/cps_typemaker', globals())

from Products.CMFCore.TypesTool import FactoryTypeInformation

def getIcon(self, relative_to_portal=0):
    """
        Returns the icon for this content object.
    """
    return self.content_icon

FactoryTypeInformation.getIcon = getIcon
