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
#"
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

"""
methods that should be unit tested here :
    manage_documentModified  ++++ need more tests
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

        """ seems like copy is not supported in test case
        liste = range(10)
        liste.reverse()
        for i in liste:
            tmaker_tool.manage_delLayout(None, None, type_name, i+1)

        self.assertEquals(count, 1)
        """

    def testChangeProperties(self):

        tmaker_tool = self.portal.portal_typemaker
        props = {}
        props['multiple_layouts'] = True
        props['flexible_aware'] = True
        props['type_prefix'] = 'mes_types_'

        tmaker_tool.manage_pchangeProperties(REQUEST=props)

        self.assertEquals(tmaker_tool.multiple_layouts, True)
        self.assertEquals(tmaker_tool.flexible_aware, True)
        self.assertEquals(tmaker_tool.type_prefix, 'mes_types_')

        self.testTypeAdding()

    def testChangeDocBaseProperties(self):
        self.testTypeAdding()
        tmaker_tool = self.portal.portal_typemaker
        type_name = tmaker_tool.type_prefix + 'TotoroPowered'
        tmaker_tool.manage_documentModified(type_id=type_name, is_addable=1,
            title='totoro lifestyle', description='totoro rulez the world')

        # check results on type
        type_tool = self.portal.portal_types
        type_factory = type_tool[type_name]

        self.assertEquals(type_factory.title, 'totoro lifestyle')
        self.assertEquals(type_factory.description, 'totoro rulez the world')


    def testaddDocElements(self):
        self.testTypeAdding()

        tmaker_tool = self.portal.portal_typemaker

        action = 'add'
        type_name = tmaker_tool.type_prefix + 'TotoroPowered'

        # add 'empty widget'
        tmaker_tool.manage_documentModified(type_id=type_name, action=action,
          new_widget_title='Totoro string widget',
          new_widget_type='String Widget')

        # check results on type
        type_layouts = self.portal.portal_layouts
        type_layout = type_layouts[type_name+'_1']

        found = False
        for id, item in type_layout.objectItems():

            if item.id == 'w__Totoro_string_widget':
                found = True
                self.assertEquals(item.title, 'Totoro string widget')
                break

        self.assert_(found)

    def testallWidgetTypes(self):
        self.testTypeAdding()

        tmaker_tool = self.portal.portal_typemaker

        action = 'add'
        type_name = tmaker_tool.type_prefix + 'TotoroPowered'

        # add 'empty widget'
        types = self.portal.portal_widget_types

        for id, type in types.objectItems():
            #raise str((type._properties))
            tmaker_tool.manage_documentModified(
                type_id=type_name, 
                action=action,
                new_widget_title='Totoro '+str(id),
                new_widget_type=type.id)

            # check results on type
            type_layouts = self.portal.portal_layouts
            type_layout = type_layouts[type_name + '_1']

            wid = 'w__Totoro '+str(id)
            wid = wid.replace(' ', '_')

            found = False
            for item_id, item in type_layout.objectItems():

                if item.id == wid:
                    found = True
                    self.assertEquals(item.title, 'Totoro ' + str(id))
                    break

            self.assert_(found)

    def test_listWidgets(self):
        tmaker_tool = self.portal.portal_typemaker
        wlist = tmaker_tool._listWidgets()
        self.assertNotEquals(wlist, [])

    def test_typeFilters(self):
        tmaker_tool = self.portal.portal_typemaker
        wlist = tmaker_tool.listWidgetTypes()

        for element in wlist:
            self.assertNotEquals(element['id'], 'Search Widget')

        tmaker_tool.type_filter_list.append('Int Widget')
        wlist = tmaker_tool.listWidgetTypes()
        for element in wlist:
            self.assertNotEquals(element['id'], 'Int Widget')

def test_suite():
    suites = [unittest.makeSuite(TestTypeMakerTool)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
