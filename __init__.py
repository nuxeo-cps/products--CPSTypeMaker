
from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory('skins/cps_typemaker', globals())

from Products.CMFCore.TypesTool import FactoryTypeInformation

def getIcon(self, relative_to_portal=0):
    """
        Returns the icon for this content object.
    """
    return self.content_icon

FactoryTypeInformation.getIcon = getIcon


from Products.CMFCore.CMFCorePermissions import ManagePortal
from AccessControl.PermissionRole import PermissionRole

from Products.CPSSchemas.Layout import Layout
Layout.setLayoutDefinition__roles__ = PermissionRole(ManagePortal)

def getFlexibleWidgetsDict(self):
    info = {}
    for item in self.flexible_widgets:
        v = item.split(':')
        if len(v) == 2:
            num = int(v[1])
        else:
            num = None
        info[v[0]] = num        
    return info

Layout.getFlexibleWidgetsDict = getFlexibleWidgetsDict
Layout.getFlexibleWidgetsInfo__roles__ = PermissionRole(ManagePortal)

from Products.CPSCore.CPSWorkflowConfiguration import CPSWorkflowConfiguration
CPSWorkflowConfiguration.getPlacefulChainFor__roles__ = PermissionRole(ManagePortal)

from Products.CPSSchemas.Field import Field
Field.manage_addProperty__roles__ = PermissionRole(ManagePortal)

from Products.CPSSchemas.Widget import Widget
Widget.getFieldInits__roles__ = PermissionRole(ManagePortal)
Widget.getFieldTypes__roles__ = PermissionRole(ManagePortal)

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.CPSCore.utils').declarePublic('makeId')
ModuleSecurityInfo('urllib').declarePublic('quote')
ModuleSecurityInfo('urllib').declarePublic('unquote')
