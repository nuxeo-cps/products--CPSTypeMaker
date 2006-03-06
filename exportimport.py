# -*- encoding: iso-8859-15 -*-
# (C) Copyright 2006 Nuxeo SAS <http://nuxeo.com>
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
# $Id$
""" CPSTypeMaker XML Adapter.
"""
from Acquisition import aq_base
from xml.dom.minidom import Element

from zope.component import adapts
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from Products.CPSTypeMaker.interfaces import ITypeMaker

_marker = object()

TOOL = 'portal_typemaker'
NAME = 'typemaker'

def exportCPSTypeMaker(context):
    """Export user folder configuration as a set of XML files.

    Does not export the users themselves.
    """
    site = context.getSite()
    if getattr(aq_base(site), TOOL, None) is None:
        logger = context.getLogger(NAME)
        logger.info("Nothing to export.")
        return
    tool = getToolByName(site, TOOL)
    exportObjects(tool, '', context)

def importCPSTypeMaker(context):
    """Import user folder configuration from XML files.
    """
    site = context.getSite()
    if getattr(aq_base(site), TOOL, None) is None:
        logger = context.getLogger(NAME)
        logger.info("Cannot import into missing acl_users.")
        return
    tool = getToolByName(site, TOOL)
    importObjects(tool, '', context)

class CPSTypeMakerXMLAdapter(XMLAdapterBase, PropertyManagerHelpers):
    """XML importer and exporter for portal_webmail
    """
    adapts(ITypeMaker, ISetupEnviron)
    implements(IBody)
    _LOGGER_ID = NAME
    name = NAME

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractProperties())
        self._logger.info("CPSTypeMaker exported.")
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        meta_type = str(node.getAttribute('meta_type'))
        if meta_type != self.context.meta_type:
            self._logger.error("Cannot import %r into %r." %
                               (meta_type, self.context.meta_type))
            return

        if self.environ.shouldPurge():
            self._purgeProperties()
        self._initProperties(node)

    node = property(_exportNode, _importNode)
