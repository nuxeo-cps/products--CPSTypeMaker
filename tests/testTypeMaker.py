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

"""
methods that should be unit tested here :
    manage_pchangeProperties
    manage_documentModified
    manage_delWidget
    manage_flexibleModified
    manage_delLayout
    manage_delFlexibleLayout
    manage_addLayout
    manage_addFlexibleLayout
    manage_layoutModified
    manage_flexLayoutModified
    manage_deleteDocumentType
    getLayoutCount
    getFlexibleTypeLayoutCount
    manage_addDocumentType
    getFieldId
    isAddable
    listTypeActions
    listWidgetTypes
    listFlexibleWidgetTypes
    getWidgetRenderer
    getWidgetType


"""
import unittest, os.path
from CPSTypeMakerTestCase import CPSTypeMakerTestCase

class TestTypeMakerTool(CPSTypeMakerTestCase):

    def testEmptyTool(self):
        tmaker_tool = self.portal.portal_typemaker
        self.assertEquals(tmaker_tool.meta_type, 'CPS Type Maker Tool')

    def testConfigurableProperties(self):
        tmaker_tool = self.portal.portal_typemaker

        properties = tmaker_tool.getConfigurableProperties()

        # all configurable properties must have a key
        # configurablme set to 1
        for property in properties:
            self.assertEquals(property['configurable'], 1)

    def testTypeAdding(self):
        tmaker_tool = self.portal.portal_typemaker
        res = tmaker_tool.manage_addDocumentType('TotoroPowered',
            'The coolest document type ever')

        # when not asked with a request, should return 'Updated'
        self.assertEquals(res, 'Updated')


    def testTypeLayoutsAdding(self):
        self.testTypeAdding()
        #raise str(self.portal.portal_types.objectValues('CPS Flexible Type Information'))

        tmaker_tool = self.portal.portal_typemaker

        type_name = tmaker_tool.type_prefix + 'TotoroPowered'

        for i in range(10):
            tmaker_tool.manage_addLayout(None, None, type_name)

        # check layout count now (base layout + 10)
        count = tmaker_tool.getTypeLayoutCount(type_name)

        self.assertEquals(count, 11)

        ### a finir
        #for i in range(10):
        #    tmaker_tool.manage_delLayout(None, None, type_name, 1)

        #self.assertEquals(count, 1)


def test_suite():
    suites = [unittest.makeSuite(TestTypeMakerTool)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
