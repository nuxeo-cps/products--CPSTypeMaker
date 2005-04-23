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
import unittest, os.path
from CPSTypeMakerTestCase import CPSTypeMakerTestCase

from Products.CPSTypeMaker.CPSWidgetDefinition import CPSWidgetRenderer
from Products.CPSSchemas.BasicWidgets import CPSStringWidget


class TestCPSWidgetDefinitions(CPSTypeMakerTestCase):

    def testEmptyTool(self):
        """ simple instanciation
        """
        ob = CPSWidgetRenderer()
        return ob

    def test_canChange(self):
        """ trying widget fields black list
        """
        tm = self.portal.portal_typemaker
        tm.widget_filter_list = ['Fields', ]
        wrenderer = tm.widget_renderer
        self.assertEquals(wrenderer._canChange('Fields'), False)
        self.assertEquals(wrenderer._canChange('Title'), True)

    def test_render(self):
        # testing rendering (for bug #601)
        widget = CPSStringWidget('my', 'String Widget')
        widget = widget.__of__(self.portal)
        ob = CPSWidgetRenderer()
        ob = ob.__of__(self.portal)
        res = ob.render(widget)
        self.assertNotEquals(res.find('widget__description_widget'), -1)

def test_suite():
    suites = [unittest.makeSuite(TestCPSWidgetDefinitions)]
    return unittest.TestSuite(suites)

if __name__=="__main__":
    unittest.main(defaultTest='test_suite')
