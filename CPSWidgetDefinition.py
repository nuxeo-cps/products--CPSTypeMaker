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
from zLOG import LOG, DEBUG, INFO
from urllib import urlencode
from Globals import InitializeClass
from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from AccessControl import ModuleSecurityInfo
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getEngine
from Products.PageTemplates.TALES import CompilerError

from Products.CPSSchemas.PropertiesPostProcessor import PropertiesPostProcessor
# from Products.CPSSchemas.StorageAdapter import AttributeStorageAdapter
from Products.CPSSchemas.StorageAdapter import BaseStorageAdapter
from Products.CPSSchemas.DataModel import DataModel
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.Field import ReadAccessError
from Products.CPSSchemas.Field import WriteAccessError

from Products.CPSSchemas.Schema import CPSSchema
from Products.CPSSchemas.Layout import CPSLayout
from Products.CPSSchemas.Vocabulary import CPSVocabulary

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.utils import getToolByName
from cgi import escape
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject
from Acquisition import Implicit,aq_parent


class CPSWidgetRenderer(PropertiesPostProcessor, UniqueObject, Folder):
    """ this class associated with a widget instance will generate
        an automatic view based on widget properties
    """
    id = 'widget_renderer'
    portal_type = meta_type = 'CPSWidgetRenderer'
    parent = None
    widget = None
    layout = schema = None
    security = ClassSecurityInfo()

    def __init__(self):
        pass

    security.declarePrivate('_generateVocabulary')
    def _generateVocabulary(self, widget, select_variable):
        """ this generates a vocabulary
            out of infos found in the widget
        """
        vocabulary_id = widget.getId() + '_' + select_variable

        if hasattr(widget, select_variable):
            values = getattr(widget, select_variable)
        else:
            values = []

        vocabulary = CPSVocabulary(vocabulary_id, list=values)
        vocabulary = vocabulary.__of__(self)

        return vocabulary



    security.declarePrivate('_getLayout')
    def _getLayout(self):
        """creates a self generated layout for our type.
        """
        if self.layout:
            return self.layout
        else:
            widget = self.widget

            if not widget:
                return None

            wtool = getToolByName(self, 'portal_widget_types')

            layout_id = widget.getId() + '_layout'
            layout = CPSLayout(layout_id)

            #
            layout = layout.__of__(self)

            # we are going to generate a one column
            # layout render
            if widget and hasattr(widget, '_properties'):
                rows = []

                for property in widget._properties:
                    p_id = property['id']
                    p_type = property['type']
                    p_label = property['label']
                    p_mode = property['mode']

                    if property.has_key('is_required'):
                        p_required = property['is_required']
                    else:
                        p_required = False

                    # finding the right widget type from property type
                    widget_type = self._findWidgetLayoutType(p_type)

                    if p_mode == 'w':

                        # adding layout definition element
                        element = {}
                        element['widget_id'] = p_id
                        element['ncols'] = 1
                        rows.append([element,])

                        # adding widget instance to layout
                        widget_type = wtool[widget_type]

                        new_widget = widget_type.makeInstance(p_id)

                        new_widget.is_required = p_required
                        new_widget.is_i18n = 1
                        new_widget.label = p_label
                        new_widget.label_edit = p_label

                        # linking the field name
                        new_widget.fields = [p_id]

                        # in case of a selection
                        # we need to link the widget to vocab
                        if p_type == 'selection':
                            select_variable = property['select_variable']
                            new_widget.vocabulary = self._generateVocabulary(widget,
                             select_variable)
                        elif p_type == 'string':
                            new_widget.display_width = 50
                        elif p_type == 'text':
                            new_widget.width = 50


                        layout.addSubObject(new_widget)

                layoutdef = {'ncols': 1, 'rows': rows}
                layout.setLayoutDefinition(layoutdef)

            self.layout = layout
            return layout


    security.declarePrivate('_findWidgetType')
    def _findWidgetLayoutType(self, property_type):
        """ finds a widget that fits property type
            XXX this needs to be externalized
            furthermore, we need here to set up
            a trigger system based on widget name
            for example if the widget
            is "vocabulary", this should bind to a select
            widget poiting the vocabulary
        """
        if property_type == 'string':
            return 'String Widget'
        elif property_type == 'int':
            return 'Int Widget'
        elif property_type == 'tokens':
            return 'Lines Widget'
        elif property_type == 'boolean':
            return 'Boolean Widget'
        elif property_type == 'text':
            return 'Text Widget'
        elif property_type == 'selection':
            return 'Select Widget'
        elif property_type == 'float':
            return 'Float Widget'
        else:
            raise "Miss one : %s" % property_type

    security.declarePrivate('_findWidgetFieldType')
    def _findWidgetFieldType(self, property_type):
        """ finds a widget that fits property type
            XXX this needs to be externalized
            furthermore, we need here to set up
            a trigger system based on widget name
            for example if the widget
            is "vocabulary", this should bind to a select
            widget poiting the vocabulary
        """
        if property_type == 'string':
            return 'CPS String Field'
        elif property_type == 'int':
            return 'CPS Int Field'
        elif property_type == 'tokens':
            return 'CPS String List Field'
        elif property_type == 'boolean':
            return 'CPS Int Field'
        elif property_type == 'text':
            return 'CPS String Field'
        elif property_type == 'selection':
            return 'CPS String Field'
        elif property_type == 'float':
            return 'CPS Float Field'        
        else:
            raise "Miss one type : %s" % property_type



    security.declarePrivate('_getAdapters')
    def _getAdapters(self, wob, **kw):
        """Get the adapters for an entry."""
        adapters = [WidgetTypeAdapter(wob, self._getSchema(), **kw)]
        return adapters


    security.declarePrivate('_getSchemas')
    def _getSchema(self):
        """Get the schema for our typhe

        """
        if self.schema:
            return self.schema
        else:
            widget = self.widget

            if not widget:
                return None

            schema_id = widget.getId() + '_schema'

            schema = CPSSchema(schema_id)

            schema = schema.__of__(self)

            # we are going to generate a one column
            # layout render
            if widget and hasattr(widget, '_properties'):
                for property in widget._properties:
                    p_id = property['id']
                    p_type = property['type']
                    p_label = property['label']
                    p_mode = property['mode']

                    # finding the right widget type from property type
                    field_type = self._findWidgetFieldType(p_type)

                    if p_mode == 'w':
                        schema.addField(p_id, field_type)

            self.schema = schema
            return schema

    security.declarePrivate('_getDataModel')
    def _getDataModel(self, wob, check_acls=1, **kw):
        """Get the datamodel for an entry.

        Passes additional **kw to _getAdapters.
        """
        adapters = self._getAdapters(wob, **kw)
        dm = DataModel(None, adapters, context=self)

        # see later for security
        dm._check_acls = 0
        dm._fetch()
        return dm


    security.declarePublic('render')
    def render(self, widget, form=None,layout_mode='edit', layout_mode_err='edit', **kw):
        """ renders the object according
            to the associated layout an schema
        """
        # see for multiple users
        self.widget = widget

        # XXXXX empty render ?
        if not widget:
            return ''

        self._cleanInstances()


        dm = self._getDataModel(widget)
        ds = DataStructure(datamodel=dm)
        layout = self._getLayout()

        # need a try..finally here

        #layout.prepareLayoutWidgets(ds)

        for widget_id, widget in layout.items():
            if not widget.isHidden():
                widget.prepare(ds)


        if form is None:
            validate = 0
        else:
            validate = 1
            ds.updateFromMapping(form)

        layout_structure = layout.computeLayoutStructure(layout_mode, dm)

        if validate:
            ok = layout.validateLayoutStructure(layout_structure, ds,
                                                layout_mode=layout_mode, **kw)
            if ok:
                dm._commit()
            else:
                layout_mode = layout_mode_err
        else:
            ok = 1


        rendered = self._renderLayout(layout_structure, ds, is_flexible=0,
                                    layout_mode=layout_mode, ok=ok, **kw)

        self._cleanInstances()
        return rendered, ok, ds



    security.declarePrivate('_cleanInstances')
    def _cleanInstances(self):
        """ clean objects used for generation
        """
        self.layout = None
        self.schema = None

    security.declarePrivate('_renderLayout')
    def _renderLayout(self, layout_structure, datastructure, **kw):
        """Render a layout according to the defined style.

        """
        layout = layout_structure['layout']
        # Render layout structure.
        layout.renderLayoutStructure(layout_structure, datastructure, **kw)

        # Apply layout style.
        context = self
        rendered = self._renderLayoutStyle(layout, layout_structure, datastructure,
                                            context, **kw)
        return rendered


    security.declarePrivate('_renderLayoutStyle')
    def _renderLayoutStyle(self, layout, layout_structure, datastructure, context, **kw):
        """Applies the layout style method to the rendered widgets.

        Returns the rendered string.
        """
        layout_mode = kw['layout_mode']
        style_prefix = kw.get('style_prefix')
        if not style_prefix:
            style_prefix = self.style_prefix
        layout_meth =  style_prefix + layout_mode
        layout_style = getattr(context, layout_meth, None)

        if layout_style is None:
            raise ValueError("No layout method '%s' for layout '%s'" %
                             (layout_meth, self.getId()))
        # compute the flexible_widgets list
        flexible_widgets = []
        if layout_mode == 'edit':
            layout_global = layout
            widget_ids = []
            for widget_id, widget in layout.items():
                if not widget.isHidden():
                    widget_ids.append(widget_id)
            flexible_widget_ids = layout_global.getFlexibleWidgetIds()
            flexible_occurences = layout_global.getFlexibleWidgetOccurences()
            flexible_widgets = []
            i = 0
            for wid in flexible_widget_ids:
                max_widget = flexible_occurences[i]
                i += 1
                if max_widget:
                    nb_widget = 0
                    for w in widget_ids:
                        if w.startswith(wid):
                            nb_widget += 1
                    if nb_widget >= int(max_widget):
                        continue

                flexible_widgets.append(layout_global[wid])

        rendered = layout_style(layout=layout_structure,
                                datastructure=datastructure,
                                flexible_widgets=flexible_widgets,
                                **kw)
        return rendered

    security.declarePublic('hasRequiredFields')
    def hasRequiredFields(self, widget):
        """ tells if the given widget has any required fields
        """
        # check if there's any property with
        # is_required key
        for property in widget._properties:
            if property.has_key('is_required'):
                if property['is_required']:
                  return True
        return False


InitializeClass(CPSWidgetRenderer)


class WidgetTypeAdapter(BaseStorageAdapter):
    """
    This adapter gets and sets data
    from the widget type layout/schema model
    to the actual widget instance
    """
    def __init__(self,widget_object, schema, field_ids=None, **kw):
        BaseStorageAdapter.__init__(self, schema, field_ids=None, **kw)
        self.widget_ob = widget_object

    def setContextObject(self, context):
        pass

    def _getFieldData(self, field_id, field, **kw):
        if self.widget_ob is not None:

            value = getattr(self.widget_ob, field_id,None)
            LOG('_getFieldData', INFO, '%s : %s' %(field_id, str(value)))
        else:
            value = None

        return value

    def _setFieldData(self, field_id, value):
        if self.widget_ob is not None:
            self.widget_ob.manage_changeProperties(**{field_id :value })



InitializeClass(WidgetTypeAdapter)
