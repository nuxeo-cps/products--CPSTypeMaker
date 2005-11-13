# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
# Author: Lennart Regebro <regebro@nuxeo.com>
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
from Products.CMFCore.permissions import ManagePortal

from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.CPSTypeMaker.TypeMakerTool import TypeMakerTool

class CPSTypeMakerInstaller(CPSInstaller):
    pass


def install(self):

    installer = CPSTypeMakerInstaller(self, 'CPSTypeMaker')
    installer.log("Starting CPSTypeMaker install")

    portal = installer.portal

    # Skins

    skins = {
        'cps_typemaker': 'Products/CPSTypeMaker/skins/cps_typemaker',
        'cps_typemaker_icons': 'Products/CPSTypeMaker/skins/cps_typemaker_icons',
        'cps_typemaker_widgets': 'Products/CPSTypeMaker/skins/cps_typemaker_widgets',
    }
    installer.verifySkins(skins)

    installer.resetSkinCache()

    # loading schemas ans layouts used by the tool
    #installer.verifySchemas(self.getWidgetsTypesSchemas())
    #installer.verifyLayouts(self.getWidgetsTypesLayouts())
    #installer.verifyVocabularies(self.getWidgetRendererVocab())

    # adding portal_typemaker singleton tool
    installer.log("adding portal_typemaker")
    tm_tool = getattr(portal, 'portal_typemaker',None)

    if (tm_tool is None) or (tm_tool.meta_type != 'CPS Type Maker Tool'):
        if tm_tool is not None:
            try:
                installer.log("deleting old portal_typemaker")
                installer.portal.manage_delObjects(['portal_typemaker'])
            except BadRequest:
                pass

        installer.log("adding portal_typemaker")
        portal.manage_addProduct['CPSTypeMaker'].\
            addCPSTypeMakerTool()

        tm_tool = getattr(portal, 'portal_typemaker',None)

    # adding action used to call typemaker tool
    installer.verifyAction(
                'portal_actions',
                id='typemaker',
                name='Type management',
                action='string:${portal_url}/cpstypes_list',
                condition='',
                permission=ManagePortal,
                category='global',
                visible=1)


    # Set up the custom metadata schema
    installer.verifySchemas({'custom_metadata': {}})

    # Translations
    installer.setupTranslations()

    installer.finalize()

    installer.log("End of specific CPSTypeMaker install")

    return installer.logResult()
