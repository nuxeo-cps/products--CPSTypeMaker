##parameters=type_id, title=None, description=None, new_icon=None, is_addable, widgetinfo=[], new_widget_title=None, new_widget_type=None, REQUEST=None, RESPONSE=None

from Products.CPSCore.utils import makeId

def deleteWidgetFromLayout(layoutdef, widgetname):
    new_rows = []
    for row in layoutdef['rows']:
        new_widgets = []
        for widget in row:
            if widget['widget_id'] != widgetname:
                new_widgets.append(widget)
        if new_widgets:
            new_rows.append(new_widgets)
    layoutdef['rows'] = new_rows
    

action = None
for key in REQUEST.keys():
    if key.startswith('action_'):
        action = key[7:] # remove the 'action_'-part
        break
       
if not action:
    raise ValueError('No action specified')

portal_status_message = []
layout = context.portal_layouts[type_id]
layoutdef = layout.getLayoutDefinition()
defs = context.cpstypes_get_definitions()
new_widget_id = makeId(new_widget_title)
if type_id != defs['metadata_layout']:
    # When the metadata layout is edited, there is no type to manage
    ttool = context.portal_types
    type = ttool[type_id]
    for actype in defs['add_in_types']:
        typeobj = ttool[actype]
        workspaceACT = list(typeobj.allowed_content_types)
        if is_addable:
            if type_id not in  workspaceACT:
                workspaceACT.append(type_id)
        else:
            if type_id in  workspaceACT:
                workspaceACT.remove(type_id)
        typeobj.manage_changeProperties(allowed_content_types = workspaceACT)

    if title is not None:
        props = {}
        for id, value in type.propertyItems():
            props[id] = value

        props['title'] = title
        props['description'] = description

        if new_icon and new_icon.read(1) != '':
            new_icon.seek(0)
            icon_id = type_id + '_icon' 
            props['content_icon'] = icon_id
            customskin = context.portal_skins.custom
            if hasattr(customskin, icon_id):
                customskin[icon_id].manage_upload(new_icon)
            else:
                customskin.manage_addFile(icon_id, new_icon, title)

    type.manage_changeProperties(**props)

for each in widgetinfo:
    widgetname = each['name']
    widgetid = each['id']
    is_selected = each.get('is_selected',0)
    indexed = each.get('indexed', 0)
    widget = layout[widgetid]
    if widget.fields != ['?']:
        field = context.cpstypes_get_field(type_id, widget)
        schemaid = field.aq_parent.getId()
        if schemaid == 'metadata':
            # Don't modify the special metadata schema
            schema = None
        else:
            schema = context.portal_schemas[schemaid]
    else:
        field = None
        schema = None
    
    if action == 'delete' and is_selected:    
        if schema and schema.has_key('f__' + widgetname):
            schema.manage_delObjects('f__' + widgetname)
            for num in range(1, len(widget.getFieldTypes())):
                schema.manage_delObjects('f__%s_f%d' % (widgetname, num))
        
        deleteWidgetFromLayout(layoutdef, widgetname)
        layout.manage_delObjects([widgetid])
    else:
        # Update widget data
        kw = {'label_edit': each['title'],
              'is_required': each.get('required',0),
              'size_max': each['size']
             } 
        if each.get('show_in_view'):
            kw['hidden_layout_modes'] = defs['hidden_layout_modes']
        else:
            kw['hidden_layout_modes'] = ['view']+defs['hidden_layout_modes']

        widget.manage_changeProperties(**kw)
        # Update indexing:
        if field:
            field.manage_changeProperties(is_searchabletext=indexed)
            if type_id == defs['metadata_layout']:
                # Indexed metadatas should also have an index of their own.
                fieldid = field.getFieldId()
                catalog = context.portal_catalog
                indexes = catalog.indexes()
                if indexed and fieldid not in indexes:
                    # Add as index
                    catalog.addIndex(fieldid, 'TextIndex')
                if not indexed and fieldid in indexes:
                    catalog.delIndex(fieldid)    
               

if action == 'add' and new_widget_id:
    kw = {'fields': [new_widget_id],
          'label_edit': new_widget_title,
         }

    if hasattr(layout, 'w__'+new_widget_id):
        portal_status_message.append('field_already_exists')

    else:
        widget = layout.manage_addCPSWidget(new_widget_id, new_widget_type, **kw)
        layoutdef = layout.getLayoutDefinition()
        layoutdef['rows'].append([{'ncols': 1, 'widget_id': new_widget_id}])

        try:
            context.cpstypes_get_field(type_id, widget)
        except AttributeError:
            # The field does not exist. We should add it.
            if type_id == defs['metadata_layout']:
                schemaid = None
                for each in defs['metadata_schemas']:
                    if each != 'metadata': # Skip the special 'metadata' schema
                        schemaid = each
                        break
                if schemaid is None:
                    raise "Configuration includes no custom metadata schema."
            else:
                schemaid = type_id

            schema = context.portal_schemas[schemaid]

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

                if type_id == defs['metadata_layout'] and \
                   field_inits and field_inits[0].get('is_searchabletext', 0):
                    catalog = context.portal_catalog
                    catalog.addIndex(new_widget_id, 'TextIndex')

# And finally save the new layout
layout.setLayoutDefinition(layoutdef)
if portal_status_message:
    portal_status_message = '\n'.join(portal_status_message)
    portal_status_message = '&portal_status_message=' + portal_status_message
else:
    portal_status_message = ''
    
return RESPONSE.redirect('cpstypes_edit?type_id='+type_id+portal_status_message)

