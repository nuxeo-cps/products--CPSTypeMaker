#!/usr/bin/python
# -*- encoding: iso-8859-15 -*-
# (C) Copyright 2003 Nuxeo SARL <http://nuxeo.com>
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
from zLOG import LOG, DEBUG,INFO
from urllib import quote
from cgi import escape
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getEngine
from Acquisition import aq_get
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.Image import Image
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.CMFCorePermissions import ManagePortal
#from Products.CPSTypeMaker.CPSWidgetDefinition import CPSWidgetDefinition
from Products.CPSTypeMaker.CPSWidgetDefinition import CPSWidgetRenderer
from Products.CPSCore.utils import makeId
from Products.CPSSchemas.DataStructure import DataStructure
from Products.CPSSchemas.DataModel import DataModel
from Products.CPSCore.CPSBase import CPSBaseFolder
from Products.CPSCore.ProxyBase import ProxyFolder
from Products.CPSSchemas.PropertiesPostProcessor import PropertiesPostProcessor
from Products.CPSSchemas.WidgetTypesTool import WidgetTypeRegistry

import ExtensionClass
"""
TypeMakerTool depends on these tools :

    portal_layouts
    portal_schemas
    portal_types
    portal_url
    Localizer
    portal_catalog

"""

class TypeMakerTool(UniqueObject, Folder, PropertiesPostProcessor):
    """ TypeMakerTool
        this tool store widget types
        defined in CPSWidgetDefinition
    """
    id = 'portal_typemaker'
    meta_type = 'CPS Type Maker Tool'

    # TO be externalized
    default_preview = 'rien.'

    security = ClassSecurityInfo()

    _propertiesBaseClass = Folder
    _properties = Folder._properties + (
        {'id': 'multiple_layouts', 'type': 'boolean', 'mode': 'w',
         'label': "Multiple Layouts"},
        {'id': 'type_prefix', 'type': 'string', 'mode': 'w',
         'label': "Id prefix for TypeMaker types"},
        {'id': 'style_prefix', 'type': 'string', 'mode': 'w',
         'label': "Id prefix for TypeMaker style"},
        {'id': 'base_schemas', 'type': 'tokens', 'mode': 'w',
         'label': "Base schemas"},
        {'id': 'base_layouts', 'type': 'tokens', 'mode': 'w',
         'label': "Base Layout"},
        {'id': 'add_in_types', 'type': 'tokens', 'mode': 'w',
         'label': "Add in types"},
        {'id': 'metadata_layout', 'type': 'string', 'mode': 'w',
         'label': "Metadata layout"},
        {'id': 'metadata_schemas', 'type': 'tokens', 'mode': 'w',
         'label': "Metadata schemas"},
        {'id': 'immediate_view', 'type': 'string', 'mode': 'w',
         'label': "Immediate View"},
        {'id': 'hidden_layout_modes', 'type': 'tokens', 'mode': 'w',
         'label': "Hidden layout modes"} ,
        {'id': 'max_rows', 'type': 'int', 'mode': 'w',
         'label': "Maximum number of rows"} ,
        {'id': 'process_before_t', 'type': 'string', 'mode': 'w',
         'label': "Process before type publish state changes"} ,
        {'id': 'process_after_t', 'type': 'string', 'mode': 'w',
         'label': "Process after type publish state changes"} ,
        )

    multiple_layouts = True
    type_prefix = 'simpletype_'
    style_prefix = 'layout_default_tab_'
    base_schemas  =  ['metadata', 'common']
    base_layouts  = ['common']
    add_in_types  =  ['Workspace', 'Section']
    metadata_layout = 'metadata'
    metadata_schemas = ['metadata', 'common']
    immediate_view = 'cpsdocument_view'
    hidden_layout_modes = []
    max_rows = 4

    process_after_t = ''
    process_before_t = ''

    _properties_post_process_tales = (
        ('process_after_t', 'process_after_tc_'),
        ('process_before_t', 'process_before_tc_'),
        )

    process_after_tc_ = None
    process_before_tc_ = None

    # XXXX this needs to be externalized
    workflow_list = {'workspaces': 'workspace_content_wf',
        'sections': 'section_content_wf',}

    widget_renderer = CPSWidgetRenderer()

    def __init__(self):
        """
        initialize object
        """
        pass

    #
    # APIs
    #
    # XXX needs to be security-leveled
    # see for naming conventions (manage_)
    def _createExpressionContext(self, type_id, ac_type, state, context):
        """Create an expression context """
        mapping = {}
        mapping.update({
            'type_id': type_id,
            'ac_type': ac_type,
            'state' : state,
            'context': context,
            'portal': getToolByName(self, 'portal_url').getPortalObject(),
            })
        return getEngine().getContext(mapping)

    security.declarePrivate('processBeforeTypeChange')
    def processBeforeTypeChange(self, type_id, ac_type, state, context):
        """
            Calls a script or an expression
            before a Type state change
        """
        self._postProcessProperties()

        if not self.process_before_tc_:

            return state

        expr_context = self._createExpressionContext(type_id, ac_type, state, context)

        return self.process_before_tc_(expr_context)


    security.declarePrivate('processAfterTypeChange')
    def processAfterTypeChange(self, type_id, ac_type, state, context):
        """
            Calls a script or an expression
            after Type state change
        """
        self._postProcessProperties()

        if not self.process_after_tc_:
            return state

        expr_context = self._createExpressionContext(type_id, ac_type, state, context)

        return self.process_after_tc_(expr_context)

    security.declarePublic('manage_delWidget')
    def manage_delWidget(self,type_id, widget_id, widget_name, REQUEST=None, RESPONSE=None):
        """ used to delete a widget from all layouts
        """
        portal_layouts = getToolByName(self, 'portal_layouts')
        portal_schemas = getToolByName(self, 'portal_schemas')
        portal_status_message = ''
        tagger = '#main'
        layout_count = self.getTypeLayoutCount(type_id)

        for i in range(layout_count):
            current_id = type_id + '_' + str(i+1)
            layout = portal_layouts[current_id]
            widget = layout[widget_id]
            field = self.getFieldId(type_id, widget)
            schemaid = field.aq_parent.getId()
            if schemaid == 'metadata':
                schema = None
            else:
                schema = portal_schemas[schemaid]

            self._deleteWidget(layout, schema, widget, widget_id, widget_name)

        if RESPONSE:
            RESPONSE.redirect('cpstypes_edit?type_id='+
                type_id+portal_status_message+tagger)


    security.declarePublic('manage_documentModified')
    def manage_documentModified(self,type_id, is_addable=None,title=None, description=None,
                         new_icon=None,  widgetinfo=[], new_widget_title=None,
                         new_widget_type=None, REQUEST=None, RESPONSE=None, action=None):
        """ this function is used to
            update a Document Type
        """
        tagger = '#main'

        if REQUEST is not None and action is None:
            for key in REQUEST.keys():
                if key.startswith('action_'):
                    action = key[7:] # remove the 'action_'-part
                    break


        if not action:
            raise ValueError('No action specified')

        portal_layouts = getToolByName(self, 'portal_layouts')
        portal_schemas = getToolByName(self, 'portal_schemas')


        portal_status_message = ''

        layout_count = self.getTypeLayoutCount(type_id)

        for i in range(layout_count):
            current_id = type_id + '_' + str(i+1)

            layout = portal_layouts[current_id]
            layoutdef = layout.getLayoutDefinition()

            if not new_widget_title:
                new_widget_title = ''

            new_widget_id = makeId(new_widget_title)

            #if type_id != self.metadata_layout:
                # When the metadata layout is edited, there is no type to manage

            if (type_id != self.metadata_layout):
                self._changeDocumentTypeProperties(type_id, is_addable, title,
                    description, new_icon)

            for each in widgetinfo:

                widgetname = each['name']
                widgetid = each['id']
                is_selected = each.get('is_selected',0)
                indexed = each.get('indexed', 0)
                widget = layout[widgetid]

                if widget.fields != ['?']:

                    field = self.getFieldId(type_id, widget)

                    schemaid = field.aq_parent.getId()

                    if schemaid == 'metadata':
                        # Don't modify the special metadata schema
                        schema = None
                    else:
                        schema = portal_schemas[schemaid]
                else:
                    field = None
                    schema = None

                if action == 'delete' and is_selected:
                    self._deleteWidget(layout, schema, widget, widgetid, widgetname)
                else:
                    # Update widget data
                    self._updateWidget(widget, type_id, each, field, indexed)


            if action == 'add' and new_widget_id:
                res = self._addwidget(layout, type_id, new_widget_id,
                    new_widget_title, new_widget_type)

                portal_status_message = portal_status_message + res
                tagger = '#components'

            # And finally save the new layout
            layout.setLayoutDefinition(layoutdef)

        if portal_status_message:
            portal_status_message = '\n'.join(portal_status_message)
            portal_status_message = '&portal_status_message=' +\
                portal_status_message
        else:
            portal_status_message = ''

        return RESPONSE.redirect('cpstypes_edit?type_id='+
            type_id+portal_status_message+tagger)


    security.declarePublic('manage_flexibleModified')
    def manage_flexibleModified(self,type_id, widgetinfo=[], new_widget_title=None,
        new_widget_type=None, REQUEST=None, RESPONSE=None, action=None):
        """ this is used to update a flexible type
            content
        """
        portal_status_message = ''

        if not action:
            for key in REQUEST.keys():

                if key.startswith('action_'):
                    action = key[7:] # remove the 'action_'-part
                    break

        if not action:
            raise ValueError('No action specified')

        ltool = getToolByName(self, 'portal_layouts')
        ttool = getToolByName(self, 'portal_types')
        urltool = getToolByName(self, 'portal_url')


        type_prefix = self.type_prefix

        layout_count = self.getTypeLayoutCount(type_id)

        for i in range(layout_count):

            flex_id = type_prefix + 'flexible_' + type_id[len(type_prefix):] \
                + '_' + str(i+1)

            layout = ltool[flex_id]
            typeob = ttool[type_id]
            portal_status_message = []

            if not new_widget_title:
                new_widget_title = ''

            new_widget_id = makeId(new_widget_title)


            flexible_widgets = []

            for each in widgetinfo:
                widgetname = each['name']
                widgetid = each['id']
                widget_repeats = each.get('repeats')

                is_selected = each.get('is_selected',0)
                widget = layout[widgetid]

                if action == 'delete' and is_selected:
                    layout.manage_delObjects([widgetid])
                else:
                    # Update widget data
                    kw = {'label_edit': each['title'],
                        'title': each['title'],
                        'size_max': each['size'],
                        }
                    widget.manage_changeProperties(**kw)
                    if widget_repeats and int(widget_repeats) > 0:
                        winfo = widgetname + ':' + str(widget_repeats)
                    else:
                        winfo = widgetname
                    flexible_widgets.append(winfo)


            if action == 'add' and new_widget_id:
                kw = {'fields': ['?'],
                    'label_edit': new_widget_title,
                    'title': new_widget_title,
                    }

                if hasattr(layout, 'w__'+new_widget_id):
                    portal_status_message.append('field_already_exists')

                else:
                    widget = layout.manage_addCPSWidget(new_widget_id,
                        new_widget_type, **kw)

                    flexible_widgets.append(new_widget_id)

            layout.manage_changeProperties(flexible_widgets=flexible_widgets)
            if flexible_widgets:
                typeob.manage_changeProperties(flexible_layouts=flex_id + ':' +
                    flex_id)
            else:
                typeob.manage_changeProperties(flexible_layouts='')

        if portal_status_message:
            portal_status_message = '\n'.join(portal_status_message)
            portal_status_message = '&portal_status_message=' +\
                portal_status_message
        else:
            portal_status_message = ''


        return RESPONSE.redirect('cpstypes_edit_flexible?type_id='+\
            str(type_id)+portal_status_message)


    def _findDirectMoving(self, kw):
        """
        finds a possible move with a given direction
        """
        direction_headers = ['up_','down_','left_','right_']
        for element in kw.keys():
            for header in direction_headers:
                len_header = len(header)
                if element.startswith(header) and \
                    (len(element) > len_header):
                    founded_field = element[len_header:].split('_')
                    if len(founded_field) > 1:
                        row = int(founded_field[0]) - 1
                        cell = int(founded_field[1]) - 1
                        direction = direction_headers.index(header)
                        return row, cell, direction
        return -1, -1, None

    def _findRowToAdd(self, kw):
        """
            finds a row to add
        """
        header = 'addnamedrow_'
        len_header = len(header)

        for element in kw.keys():
            if element.startswith(header) and \
                (len(element) > len_header):
                founded_field = element[len_header:].strip()
                if founded_field <> '':
                    return founded_field
                else:
                    return None
        return None



    def _fillDefaultValues(self, layout, document):
        """ this fills a document width default values
        """
        ti = document.getTypeInfo()
        dm = ti.getDataModel(document)

        # getting field list
        kw = {}

        # XXX work in process
        for widget_id, widget in layout.items():
            if not widget.isHidden():
                if widget_id == 'Photo':
                    kw[widget_id] = None
                else:
                    # gets default value from wodget type file
                    type_content = self._getDefaultValue(widget.meta_type)
                    kw[widget_id] = type_content
        document.edit(**kw)


    def _layoutDirectMoving(self, layout, row, cell, direction):
        """ move cells around"""
        # first of all let's find layout boudnaries
        layoutdef = layout.getLayoutDefinition()
        rows = layoutdef['rows']

        numlines = len(rows)

        up_row = -1
        up_cell = -1

        # up
        if direction == 0:
            if row > 0:
                # let's find the cell
                up_nrow = rows[row-1]
                up_row = row - 1
                len_up_nrow = len(up_nrow)

                if cell >= len_up_nrow:
                    if len_up_nrow > 0:
                        up_cell = len_up_nrow - 1
                else:
                    up_cell = cell

        # down
        elif direction == 1:
            if row < numlines -1:
                up_nrow = rows[row+1]
                up_row = row + 1
                len_up_nrow = len(up_nrow)

                if cell >= len_up_nrow:
                    if len_up_nrow > 0:
                        up_cell = len_up_nrow - 1
                else:
                    up_cell = cell

        # left
        elif direction == 2:
            if cell > 0:
                up_row = row
                up_cell = cell - 1

        # right
        elif direction == 3:
            if cell < len(rows[row]) -1:
                up_row = row
                up_cell = cell + 1

        if (up_row <> -1) and (up_cell <> -1) and \
             (up_row<len(rows)) and (up_cell<len(rows[up_row])) :

            widget_dest_id = rows[up_row][up_cell]['widget_id']
            widget_orig_id = rows[row][cell]['widget_id']
            rows[up_row][up_cell]['widget_id'] = widget_orig_id
            rows[row][cell]['widget_id'] = widget_dest_id
            layoutdef['rows'] = rows
            layout.setLayoutDefinition(layoutdef)

    security.declarePublic('manage_delLayout')
    def manage_delLayout(self, REQUEST, RESPONSE, type_id, layout_index):
        """ deletes a layout
        """
        # we don't want to let the user delete main layout
        nothing_deleted = True
        if layout_index > 1:
            type_prefix = self.type_prefix

            ltool = getToolByName(self, 'portal_layouts')
            # does the layout exists ?
            ob_id = type_id + '_' + str(layout_index)
            if hasattr(ltool, ob_id):
                # delete
                ltool.manage_renameObject(ob_id, ob_id+'_del')

                # let's rename next layouts
                next_index = int(layout_index) + 1
                while hasattr(ltool,type_id + '_' + str(next_index)):
                    old = type_id + '_' + str(next_index)
                    new = type_id + '_' + str(next_index-1)

                    LOG('renaming', INFO, 'old: %s new %s' % (old, new))

                    ltool.manage_renameObject(old, new)
                    next_index += 1

                ltool.manage_delObjects([ob_id+'_del'])

                nothing_deleted = False

            # same work for flexibles

            ob_id = type_id + '_' + str(layout_index)
            ob_flex_id = ob_id.replace(type_prefix, type_prefix + 'flexible_')


            if hasattr(ltool, ob_flex_id):
                # delete
                ob_or = ob_flex_id
                ltool.manage_renameObject(ob_flex_id, ob_flex_id+'_del')

                # let's rename next layouts
                next_index = int(layout_index) + 1
                ob_id = type_id + '_' + str(next_index)
                ob_flex_id = ob_id.replace(type_prefix, type_prefix + 'flexible_')
                ob_old_id = type_id + '_' + str(next_index+1)
                ob_old_flex_id = ob_old_id.replace(type_prefix, type_prefix + 'flexible_')

                while hasattr(ltool, ob_flex_id):
                    if hasattr(ltool, ob_old_flex_id):
                        ltool.manage_renameObject(ob_old_flex_id, ob_flex_id)
                    next_index += 1
                    ob_id = type_id + '_' + str(next_index)
                    ob_flex_id = ob_id.replace(type_prefix, type_prefix + 'flexible_')
                    ob_old_id = type_id + '_' + str(next_index+1)
                    ob_old_flex_id = ob_old_id.replace(type_prefix, type_prefix + 'flexible_')

                # delete
                ltool.manage_delObjects([ob_or+'_del'])

        if RESPONSE:
            Localizer = getToolByName(self, 'Localizer')

            if Localizer:
                mcat = Localizer.default
                #message = mcat('psm_changed')
                message = 'psm_changed'
            else:
                message = ''

            urltool = getToolByName(self, 'portal_url')
            RESPONSE.redirect(
                urltool()+
                    '/cpstypes_layout_edit?type_id=%s&portal_status_message=%s'
                     % (type_id, message))
        else:
            return not nothing_deleted

    security.declarePublic('manage_addLayout')
    def manage_addLayout(self, REQUEST, RESPONSE, type_id):
        """ adds an extra layout
        """
        style_prefix = self.style_prefix
        type_prefix  = self.type_prefix

        ltool = getToolByName(self, 'portal_layouts')
        ttool = getToolByName(self, 'portal_types')


        # let's find the next index
        current_index = 1
        while hasattr(ltool,type_id + '_' + str(current_index)):
            current_index += 1

        new_id = type_id + '_' +str(current_index)
        new_flex_id = new_id.replace(type_prefix, type_prefix + 'flexible_')

        layout = ltool.manage_addCPSLayout(new_id)
        layout.manage_changeProperties(style_prefix=style_prefix)

        flexlayout = ltool.manage_addCPSLayout(new_flex_id)
        flexlayout.manage_changeProperties(style_prefix=style_prefix)

        # if it's secondary layouts
        # we want to copy widgets from first layout
        if self.getTypeLayoutCount(type_id) > 0:
            base_type_id = type_id + '_1'
            base_flex_id = base_type_id.replace(type_prefix, type_prefix
                + 'flexible_')

            primary_layout = ltool[base_type_id]
            self._copyWidgets(primary_layout, layout)
            primary_flx_layout = ltool[base_type_id]
            self._copyWidgets(primary_flx_layout, flexlayout)


        type_tool = ttool[type_id]

        if new_id not in type_tool.layouts:
            type_tool.layouts = list(type_tool.layouts) + [new_id]

        if new_flex_id not in type_tool.schemas:
            type_tool.layouts = list(type_tool.layouts) + [new_flex_id]

        if RESPONSE:
            Localizer = getToolByName(self, 'Localizer')

            if Localizer:
                mcat = Localizer.default
                #message = mcat('psm_changed')
                message = 'psm_changed'
            else:
                message = ''

            urltool = getToolByName(self, 'portal_url')
            RESPONSE.redirect(
                urltool()+
                    '/cpstypes_layout_edit?type_id=%s&layout_index=%s&portal_status_message=%s'
                     % (type_id, current_index, message))
        else:
            return new_id, new_flex_id

    security.declarePublic('manage_layoutModified')
    def manage_layoutModified(self,REQUEST, RESPONSE, type_id, layout_index=1):
        """ called when a layout is modified
        """

        delcell = 0
        splitcell = 0
        widencell = 0
        shrinkcell = 0
        used_widgets = []
        duplicate_widgets = []
        ltool = getToolByName(self, 'portal_layouts')
        Localizer = getToolByName(self, 'Localizer')
        urltool = getToolByName(self, 'portal_url')
        message = ''

        layout_id = type_id + '_' + str(layout_index)

        layout = ltool[layout_id]
        kw = {}
        kw.update(REQUEST.form)

        row_to_add = self._findRowToAdd(kw)

        dm_row, dm_cell, dm_direction = self._findDirectMoving(kw)

        if kw.has_key('autolayout') :

            # makes an auto layout
            # at this time it's just a one column thing
            # but could be more elaborated later
            layoutdef = {'ncols': 1, 'rows': []}

            rows = []

            for item in layout.objectIds():
                element = {}
                # cutting off the "w__" thing
                element['widget_id'] = item[3:]
                element['ncols'] = 1
                rows.append([element])

            layoutdef['rows'] = rows

            layout.setLayoutDefinition(layoutdef)


        elif row_to_add is not None:
            # adds a row and fill it
            layoutdef = layout.getLayoutDefinition()
            rows = layoutdef['rows']
            new_element = {}
            new_element['widget_id'] = row_to_add
            new_element['ncols'] = 1
            rows.append([new_element])

            layout.setLayoutDefinition(layoutdef)

        elif dm_row <> -1:
            self._layoutDirectMoving(layout, dm_row, dm_cell, dm_direction)

        else:
            # XXX this should be refactored
            # to directly set the layout definition
            # like in other case
            # to avoid calling manage_changeLayout
            layoutdef = layout.getLayoutDefinition()
            rows = layoutdef['rows']
            row = 1

            while kw.has_key('cell_%d_1' % row):
                cell = 1
                while kw.has_key('cell_%d_%d' % (row, cell)):

                    widget_id = kw.get('cell_%d_%d' % (row, cell), '')

                    # inline deletion
                    if kw.has_key('del_check_%d_%d' %(row, cell)) :
                        kw['check_%d_%d' %(row, cell)] = '1'
                        delcell = 1
                    elif kw.has_key('split_check_%d_%d' %(row, cell)) :

                        current_max = len(rows[row-1])

                        if current_max < self.max_rows:
                            kw['check_%d_%d' %(row, cell)] = '1'
                            splitcell = 1
                        else:
                            message = 'psm_maxwidth'

                    elif kw.has_key('widen_check_%d_%d' %(row, cell)) :
                        kw['check_%d_%d' %(row, cell)] = '1'
                        widencell = 1
                    elif kw.has_key('shrink_check_%d_%d' %(row, cell)) :
                        kw['check_%d_%d' %(row, cell)] = '1'
                        shrinkcell = 1
                    else:
                        used_widgets.append(widget_id)

                    cell += 1
                row += 1

            layout.manage_changeLayout(widencell=widencell,
                shrinkcell=shrinkcell,splitcell=splitcell,delcell=delcell,**kw)

        if Localizer:
            mcat = Localizer.default
            if duplicate_widgets:
                message = quote(mcat('psm_duplicate_widgets') +
                ','.join(duplicate_widgets))
            else:
                if message == '':
                    message = 'psm_changed'
        else:
            message = ''

        RESPONSE.redirect(
            urltool()+
                '/cpstypes_layout_edit?type_id=%s&layout_index=%s&portal_status_message=%s' % (
                type_id, layout_index, message))

    def _renameDocumentTypeElement(self, container, id):
        """ renames an object
        """
        if hasattr(container, id):
            new_id = 'old_' + id
            i = 0

            while hasattr(container, new_id):
                new_id= 'old_' + id + str(i)
                i+=1

            container.manage_renameObject(id, new_id)



    security.declarePublic('manage_deleteDocumentType')
    def manage_deleteDocumentType(self, ids, RESPONSE=None):
        """ called when a document type is deleted
        """
        # this is a fake deletion
        # (safer for portal content)
        ttool = getToolByName(self, 'portal_types')
        stool = getToolByName(self, 'portal_schemas')
        ltool = getToolByName(self, 'portal_layouts')
        utool = getToolByName(self, 'portal_url')


        for id in ids:
            self.processBeforeTypeChange(id, 'all', False, self)
            try:
                type_id = id
                flex_id = 'flexible_' + id

                # removing from allowed content types
                for type in self.add_in_types:
                    typeobj = ttool[type]
                    workspaceACT = list(typeobj.allowed_content_types)

                    if type_id in workspaceACT:
                        workspaceACT.remove(type_id)

                    typeobj.manage_changeProperties(allowed_content_types=workspaceACT)

                # renaming types
                self._renameDocumentTypeElement(ttool, type_id)
                self._renameDocumentTypeElement(stool, type_id)
                self._renameDocumentTypeElement(stool, flex_id)
                self._renameDocumentTypeElement(ltool, type_id)
                self._renameDocumentTypeElement(ltool, flex_id)
            finally:
                self.processAfterTypeChange(id, 'all', False, self)

        psm = 'document types deleted'

        if RESPONSE:
            return RESPONSE.redirect(utool() +
                '/cpstypes_list?portal_status_message=%s' % psm)
        else:
            return 'Updated'

    security.declarePublic('getLayoutCount')
    def getTypeLayoutCount(self, type_id):
        """
            retrieves a type layout count
        """
        ltool = getToolByName(self, 'portal_layouts')
        count = 0
        current_index = 1


        while hasattr(ltool,str(type_id) + '_' + str(current_index)):
            count += 1
            current_index += 1

        return count


    security.declarePublic('manage_addDocumentType')
    def manage_addDocumentType(self,title,description,RESPONSE=None):
        """ called when a document type is added
        """
        id = makeId(title)

        # getting tool links
        ttool = getToolByName(self, 'portal_types')
        stool = getToolByName(self, 'portal_schemas')
        ltool = getToolByName(self, 'portal_layouts')
        utool = getToolByName(self, 'portal_url')

        # getting values out of tmaker
        prefix = self.type_prefix
        base_layouts = self.base_layouts
        base_schemas = self.base_schemas
        add_in_types = self.add_in_types
        style_prefix = self.style_prefix
        type_actions = self.listTypeActions()
        immediate_view = self.immediate_view

        type_id = prefix + id
        flex_id = prefix + 'flexible_' + id

        if hasattr(ttool, type_id):
            if RESPONSE:
                return RESPONSE.redirect(utool() + \
                 '/cpstypes_add_form?portal_status_message=type_already_exists')
            else:
                return

        ti = ttool.addFlexibleTypeInformation(id=type_id)
        properties = {
            'title': title,
            'description': description,
            'content_icon': 'document_icon.gif',
            'content_meta_type': 'CPS Document',
            'product': 'CPSDocument',
            'factory': 'addCPSDocument',
            'immediate_view': immediate_view,
            'global_allow': 1,
            'filter_content_types': 1,
            'allowed_content_types': (),
            'allow_discussion': 0,
            'cps_is_searchable': 1,
            'cps_proxy_type': 'document',
            'schemas': list(base_schemas) + [type_id, flex_id],
            'layouts': list(base_layouts) + [type_id+'_1', flex_id+'_1'],
            }
        ti.manage_changeProperties(**properties)

        if type_actions:
            ti.deleteActions(range(0, len(ti.listActions())))
            for action in type_actions:
                ti.addAction(**action)

        # adding first layout
        new_id, new_flexid = self.manage_addLayout(None, None, type_id)
        #layout = ltool.manage_addCPSLayout(type_id)
        #layout.manage_changeProperties(style_prefix=style_prefix)
        #flexlayout = ltool.manage_addCPSLayout(flex_id)
        #flexlayout.manage_changeProperties(style_prefix=style_prefix)

        for type in add_in_types:
            typeobj = ttool[type]
            workspaceACT = list(typeobj.allowed_content_types)
            if type_id not in  workspaceACT:
                self.processBeforeTypeChange(type, typeobj, True, self)
                try:
                    workspaceACT.append(type_id)
                    typeobj.manage_changeProperties(allowed_content_types =\
                        workspaceACT)
                finally:
                    self.processAfterTypeChange(type, typeobj, True, self)

        portal = utool.getPortalObject()

        # XXX cpstypes_get_workflows needs to be integrated in this class
        for sectionspace, workflow in self.workflow_list.items():
            wfconf = getattr(portal[sectionspace],'.cps_workflow_configuration')
            if not wfconf.getPlacefulChainFor(type_id):
                wfconf.manage_addChain(portal_type=type_id, chain=workflow)

        stool.manage_addCPSSchema(type_id)
        stool.manage_addCPSSchema(flex_id)

        if RESPONSE:
            return RESPONSE.redirect(utool() +
                '/cpstypes_edit?type_id='+type_id)
        else:
            return 'Updated'



    security.declarePublic('getFieldId')
    def getFieldId(self, schema, widget):
        """
            gives a field id for a given*
            schema and widget couple
        """
        # XXX needs protection
        fieldid = widget.fields[0]
        schemas = [schema]

        for metadata_schema in self.metadata_schemas:
             schemas.append(metadata_schema)

        stool = getToolByName(self, 'portal_schemas')

        for schemaid in schemas:
            schemaob = stool[schemaid]

            if schemaob.has_key(fieldid):
                return schemaob[fieldid]

            #raise str(schemaob.keys())

        raise AttributeError("Field %s is not found for widget %s in type %s"
            %(fieldid, widget.getId(), schema))

    security.declarePublic('isAddable')
    def isAddable(self,type_id):
        """ is this portal type is an allowed content ?
        """
        types = self.add_in_types
        ttool = getToolByName(self, 'portal_types')
        for type in types:
            typeob = ttool[type]
            if type_id in typeob.allowed_content_types:
                return 1

        return 0

    security.declarePublic('listTypeActions')
    def listTypeActions(self):
        """ will return action list
        """
        return ()




    security.declarePrivate('_listWidgets')
    def _listWidgets(self, attribute='_marker', translated = False):
        """ returns a list of ids and meta_types
            filtered if needed
            by a boolean attribute
            meta_type is translated if needeed
        """
        res = []
        portal_widget_types = getToolByName(self, 'portal_widget_types')
        Localizer = getToolByName(self, 'Localizer')
        if Localizer:
            mcat = Localizer.default

        for id, widget in portal_widget_types.objectItems():
            # theses are widget types
            if (attribute == '_marker') or not hasattr(widget, attribute)\
             or widget.is_addable:
                element = {}
                meta_type = widget.meta_type


                element['id'] = widget.getId()
                element['meta_type'] = meta_type

                """
                if meta_type.endswith(' Type'):
                    sort_key = meta_type[:len(meta_type)-5]
                else:
                    sort_key = meta_type
                """
                # see for translation
                sort_key = widget.getId()

                if translated and mcat:
                    sort_key = mcat(sort_key)

                sorter =  (sort_key, element,)
                res.append(sorter)

        res.sort()

        result = []

        for item in res:
            result.append(item[1])

        return result



    security.declarePublic('listWidgetTypes')
    def listWidgetTypes(self, translated = False):
        """ list widget types that can be used to
            create new documents types
        """
        return self._listWidgets('is_addable', translated)

    security.declarePublic('listFlexibleWidgetTypes')
    def listFlexibleWidgetTypes(self, translated = False):
        """ list widget types that can be used to
            create new documents types
        """
        return self._listWidgets('flex_is_addable', translated)


    security.declarePublic('getWidgetRenderer')
    def getWidgetRenderer(self):
        """ create a widget renderer object
            according to the given widget instance
        """
        ### XXXX we need to link the object to
        ### type maker tool
        ### otherwise some code in layout/schema
        ### mechansim won't work
        ### need to figure out how to clean it afterwards
        ### and how to make it work for several users at the same time
        if not self.widget_renderer:
            self.widget_renderer =  CPSWidgetRenderer()

        return self.widget_renderer




    security.declarePublic('getWidgetType')
    def layoutPreview(self,type_id):
        """ this renders a preview
            made up with
            widgets and the given layout
        """
        # XXXX
        # find a suitable place
        # previews are placed in portal_typemaker/.previews
        # so the tool works for homeless members too
        # member must have a home
        # in order to preview
        portal_membership = getToolByName(self, 'portal_membership')
        member_folder = portal_membership.getHomeFolder()

        if member_folder is not None:
            portal_layouts = getToolByName(self, 'portal_layouts')
            layout = portal_layouts[type_id]
            ob_id = str(type_id) + '_preview'
            ob_id = member_folder.computeId(compute_from=ob_id)
            if getattr(member_folder, ob_id, None) is not None:
                member_folder.deleteObject(ob_id)

            member_folder.invokeFactory(type_id, ob_id)

            ob = getattr(member_folder, ob_id, None)
            doc = ob.getEditableContent()
            doc.edit(Title='Preview for '+str(type_id))
            self._fillDefaultValues(layout, doc)
            member_folder.REQUEST.RESPONSE.redirect(member_folder.absolute_url()+'/'+ob_id)

    #
    # private methods
    #

    def _deleteWidgetFromLayout(self,layoutdef, widgetname):
        """
            deletes a widget from layout and schema
        """
        new_rows = []
        for row in layoutdef['rows']:
            new_widgets = []
            for widget in row:
                if widget['widget_id'] != widgetname:
                    new_widgets.append(widget)
            if new_widgets:
                new_rows.append(new_widgets)
        layoutdef['rows'] = new_rows


    def _getDefaultValue(self, meta_type):
        """ gives a default value for a widget meta_type
        """
        for widgettype_id, widgettype in self.objectItems():
            if widgettype.widget_type == meta_type:
                preview_content = widgettype.previewContent()
                return preview_content

        return ''

    security.declarePublic('hasRequiredFields')
    def hasRequiredFields(self, widget):
        """ gives a default value for a widget meta_type
        """
        return self.widget_renderer.hasRequiredFields(widget)



    def _updateWidget(self, widget, type_id, current, field, indexed):
        """ updates the widget
            according to field' content
        """
        catalog = getToolByName(self, 'portal_catalog')

        kw = {'label_edit': current['title'],
            'is_required': current.get('required',0),
            'size_max': '0'
            }
        if current.get('show_in_view'):
            kw['hidden_layout_modes'] = self.hidden_layout_modes
        else:
            kw['hidden_layout_modes'] = ['view']+\
                self.hidden_layout_modes

        widget.manage_changeProperties(**kw)
        # Update indexing:
        if field:
            field.manage_changeProperties(is_searchabletext=indexed)
            if type_id == self.metadata_layout:
                # Indexed metadatas should also have an index of their
                # own.
                fieldid = field.getFieldId()

                indexes = catalog.indexes()
                if indexed and fieldid not in indexes:
                    # Add as index
                    catalog.addIndex(fieldid, 'TextIndex')
                if not indexed and fieldid in indexes:
                    catalog.delIndex(fieldid)

    def _deleteWidget(self, layout, schema, widget, widgetid, widgetname):
        """
          deletes a widget from layout and schema
        """
        layoutdef = layout.getLayoutDefinition()

        if schema and schema.has_key('f__' + widgetname):
            schema.manage_delObjects('f__' + widgetname)
            for num in range(1, len(widget.getFieldTypes())):
                schema.manage_delObjects('f__%s_f%d' %
                    (widgetname,num))

        self._deleteWidgetFromLayout(layoutdef, widgetname)
        layout.manage_delObjects([widgetid])



    def _copyWidgets(self, from_layout, to_layout):
        """
        copies widgets from one layout to another
        """
        portal_schemas = getToolByName(self, 'portal_schemas')
        catalog = getToolByName(self, 'portal_catalog')

        for widget in from_layout.objectValues():
            widget_id = widget.getId()

            if widget_id.startswith('w__'):
                widget_id = widget_id[3:]

            widget_type = widget.widget_type
            widget_title = widget.title


            kw = {'fields': [widget_id],
                'label_edit': widget_title,
                'label': widget_title,
                'title': widget_title,
                }

            if not hasattr(to_layout, 'w__'+widget_id):
                widget = to_layout.manage_addCPSWidget('w__'+widget_id,
                    widget_type,**kw)


    def _addwidget(self, layout, type_id, new_widget_id, new_widget_title,
         new_widget_type):
        """ used to add a new widget in the given layout
            and its schemas

        """
        portal_status_message = []

        portal_schemas = getToolByName(self, 'portal_schemas')
        catalog = getToolByName(self, 'portal_catalog')

        kw = {'fields': [new_widget_id],
              'label_edit': new_widget_title,
              'label': new_widget_title,
              'title': new_widget_title,
              }

        if hasattr(layout, 'w__'+new_widget_id):
            portal_status_message.append('field_already_exists')

        else:
            widget = layout.manage_addCPSWidget(new_widget_id,
                new_widget_type,**kw)

            layoutdef = layout.getLayoutDefinition()
            layoutdef['rows'].append([{'ncols': 1, 'widget_id':
                new_widget_id}])

            try:
                self.getFieldId(type_id, widget)
            except AttributeError:
                # The field does not exist. We should add it.
                if type_id == self.metadata_layout:
                    schemaid = None
                    for each in self.metadata_schemas:
                        if each != 'metadata':
                            # Skip the special 'metadata' schema
                            schemaid = each
                            break
                    if schemaid is None:
                        raise "Configuration includes no custom metadata\
schema."
                else:
                    schemaid = type_id

                schema = portal_schemas[schemaid]

                if not schema.has_key('f__' + new_widget_id):
                    field_types = widget.getFieldTypes()
                    field_inits = widget.getFieldInits()
                    i = 0
                    for field_type in field_types:
                        # Find free field id (based on the field type name).
                        field_id = new_widget_id
                        field_ids = schema.keys()
                        n = 0
                        while field_id in field_ids:
                            n += 1
                            field_id = '%s_f%d' % (new_widget_id, n)

                        # Create the field.
                        if field_inits:
                            kw = field_inits[i]
                        else:
                            kw = {}
                        i += 1
                        schema.manage_addField(field_id, field_type, **kw)

                    if type_id == self.metadata_layout and \
                field_inits and field_inits[0].get('is_searchabletext',0):
                        catalog.addIndex(new_widget_id, 'TextIndex')

        return portal_status_message

    def _changeDocumentTypeProperties(self, type_id, is_addable=None,title=None,
        description=None, new_icon=None,):
        """
            changes Document Types infos
        """
        ttool = getToolByName(self, 'portal_types')
        skintool = getToolByName(self, 'portal_skins')

        type = ttool[type_id]
        for actype in self.add_in_types:
            typeobj = ttool[actype]
            workspaceACT = list(typeobj.allowed_content_types)
            if is_addable:
                if type_id not in  workspaceACT:
                    self.processBeforeTypeChange(type_id, actype, True, self)
                    try:
                        workspaceACT.append(type_id)
                    finally:

                        self.processAfterTypeChange(type_id, actype, True, self)
            else:
                if type_id in workspaceACT:
                    self.processBeforeTypeChange(type_id, actype, False, self)
                    try:
                        workspaceACT.remove(type_id)
                    finally:
                        self.processAfterTypeChange(type_id, actype, False, self)

            typeobj.manage_changeProperties(allowed_content_types =
                workspaceACT)

        # normalizing fields
        if title is not None:
            title = str(title)
        else:
            title = ''
        if description is not None:
            description = str(description)
        else:
            description = ''

        # changes description and/or title if needeed
        if (type.title <> title) or (type.description <> description):
            props = {}
            for id, value in type.propertyItems():
                props[id] = value

            props['title'] = title
            props['description'] = description


            if new_icon and new_icon.read(1) != '':
                new_icon.seek(0)
                icon_id = type_id + '_icon'
                props['content_icon'] = icon_id
                customskin = skintool.custom
                if hasattr(customskin, icon_id):
                    customskin[icon_id].manage_upload(new_icon)
                else:
                    customskin.manage_addFile(icon_id, new_icon, title)

            type.manage_changeProperties(**props)


InitializeClass(TypeMakerTool)

def addCPSTypeMakerTool(container, id=None, REQUEST=None, **kw):
    """Add a CPS MemberData Tool."""
    if id is None:
        id = container.computeId()
    container = container.this() # For FactoryDispatcher.

    t = TypeMakerTool()
    container._setObject(t.getId(), t)
    if REQUEST is not None:
        t = container._getOb(t.getId())
        REQUEST.RESPONSE.redirect(t.absolute_url()+'/manage_overview')

