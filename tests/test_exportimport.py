# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2004 Nuxeo SARL <http://nuxeo.com>
# Authors: Tarek Ziadé <tz@nuxeo.com>
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
"""CPSTypeMaker export / import support unit tests.

$Id$
"""
import unittest
import os
import Testing
import Zope2
Zope2.startup()

from Products.Five import zcml
from zope.app import zapi

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.testing import BodyAdapterTestCase
from Products.GenericSetup.testing import DummySetupEnviron

currentdir = os.path.dirname(__file__)
_TYPEMAKER_BODY = open(os.path.join(currentdir, 'exported.xml')).read()

class CPSTypeMakerXMLAdapterTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from Products.CPSTypeMaker.exportimport import CPSTypeMakerXMLAdapter
        return CPSTypeMakerXMLAdapter

    def setUp(self):
        import Products
        from Products.CPSTypeMaker.TypeMakerTool import TypeMakerTool
        BodyAdapterTestCase.setUp(self)
        zcml.load_config('configure.zcml',
                         Products.CPSTypeMaker)
        self._obj = TypeMakerTool()
        self._BODY = _TYPEMAKER_BODY

    def test_body_get_special(self):
        context = DummySetupEnviron()
        adapted = zapi.getMultiAdapter((self._obj, context), IBody)
        self.assertEqual(adapted.body, _TYPEMAKER_BODY)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CPSTypeMakerXMLAdapterTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
