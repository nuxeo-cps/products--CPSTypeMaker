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

import os
from zLOG import LOG, INFO, DEBUG

from Products.CPSInstaller.CPSInstaller import CPSInstaller


def install(self):

    installer = CPSInstaller(self, 'CPSTypeMaker')
    installer.log("Starting CPSTypeMaker install")

    # skins
    skins = {
        'cps_typemaker': 'Products/CPSTypeMaker/skins/cps_typemaker',
    }
    installer.verifySkins(skins)

    # action
    installer.verifyAction(
                'portal_actions',
                id='typemaker',
                name='Type management',
                action='string:${portal_url}/cpstypes_list',
                condition='',
                permission=('Manage Portal',),
                category='global',
                visible=1)

    # translations
    installer.setupTranslations()
    
    installer.finalize()
    installer.log("End of specific CPSSchemas install")
    return installer.logResult()
