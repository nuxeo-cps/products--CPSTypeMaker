#!/usr/bin/python
# -*- encoding: iso-8859-15 -*-
# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziad� <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$

from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CPSSchemas.Field import Field
from Products.CMFCore.permissions import ManagePortal
from AccessControl.PermissionRole import PermissionRole
from Products.CPSSchemas.Layout import Layout
from Products.CPSWorkflow.configuration import Configuration
from Products.CPSTypeMaker import TypeMakerTool
from Products.CMFCore.utils import ToolInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CPSSchemas.Widget import Widget
# check this
from AccessControl.Permissions import add_user_folders as AddUserFolders
from AccessControl import ModuleSecurityInfo

from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CPSCore.interfaces import ICPSSite


def getIcon(self, relative_to_portal=0):
    """
        Returns the icon for this content object.
    """
    return self.content_icon

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



FactoryTypeInformation.getIcon = getIcon
Layout.setLayoutDefinition__roles__ = PermissionRole(ManagePortal)
Layout.getFlexibleWidgetsDict = getFlexibleWidgetsDict
Layout.getFlexibleWidgetsInfo__roles__ = PermissionRole(ManagePortal)
Configuration.getPlacefulChainFor__roles__ =\
PermissionRole(ManagePortal)
Field.manage_addProperty__roles__ = PermissionRole(ManagePortal)
Widget.getFieldInits__roles__ = PermissionRole(ManagePortal)
Widget.getFieldTypes__roles__ = PermissionRole(ManagePortal)
ModuleSecurityInfo('Products.CPSCore.utils').declarePublic('makeId')
ModuleSecurityInfo('urllib').declarePublic('quote')

registerDirectory('skins', globals())

# initialistation de l'outil-container et du type WidgetType
def initialize(registrar):

    registrar.registerClass(
        TypeMakerTool.TypeMakerTool,
        permission=AddUserFolders,
        constructors=(TypeMakerTool.addCPSTypeMakerTool,),
        icon='zmi/tool.png')

    profile_registry.registerProfile('default',
                                     'CPS TypeMaker',
                                     "Profile for CPSTypeMaker.",
                                     'profiles/default',
                                     'CPSTypeMaker',
                                     EXTENSION,
                                     for_=ICPSSite)
