#!/usr/bin/python
# -*- encoding: iso-8859-15 -*-
# (C) Copyright 2004 Nuxeo SARL <http://nuxeo.com>
# Author: Tarek Ziadé <tz@nuxeo.com>
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
from Testing import ZopeTestCase
from Products.CPSDefault.tests import CPSTestCase

CPSTypeMakerTestCase = CPSTestCase.CPSTestCase


class CPSTypeMakerTestsInstaller(CPSTestCase.CPSInstaller):

    def install(self, portal_id):
        self.addUser()
        self.login()
        self.addPortal(portal_id)
        self.fixupTranslationServices(portal_id)
        self.setupTypeMaker(portal_id)
        self.logout()

    def setupTypeMaker(self, portal_id):
        portal = getattr(self.app, portal_id)
        factory = portal.manage_addProduct['CPSTypeMaker']
        factory.addCPSTypeMakerTool(portal_id)



""" setting up a portal for tests

"""
def setupPortal(PortalInstaller=CPSTypeMakerTestsInstaller):
    # Create a CPS site in the test (demo-) storage with Type Maker
    app = ZopeTestCase.app()

    if hasattr(app, 'portal'):
        app.manage_delObjects(['portal'])
    CPSTypeMakerTestsInstaller(app).install('portal')
    ZopeTestCase.close(app)




# needeed products besides cps default onces
ZopeTestCase.installProduct('CPSTypeMaker')

# sets up the portal
setupPortal()