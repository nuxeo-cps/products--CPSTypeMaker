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

layout = context.portal_layouts[type_id]
layoutdef = layout.getLayoutDefinition()
defs = context.cpstypes_get_definitions()
new_widget_id = makeId(new_widget_title)
if type_id == 'metadata':
    custom_metadata = context.cpstypes_get_definitions()['metadata_id']
    schema = context.portal_schemas[custom_metadata]
    metadata_schema = context.portal_schemas['metadata']
else:
    ttool = context.portal_types
    type = ttool[type_id]
    schema = context.portal_schemas[type_id]
    metadata_schema = None
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
    widget = layout[widgetid]
    
    if action == 'delete' and is_selected:    
        if widget.fields != ['?'] and schema.has_key('f__' + widgetname):
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
            kw['hidden_layout_modes'] = []
        else:
            kw['hidden_layout_modes'] = ['view']

        widget.manage_changeProperties(**kw)
        field = context.cpstypes_get_field(type_id, widget)
        field.manage_changeProperties(is_searchabletext=each.get('indexed', 0))
        

if action == 'add' and new_widget_id:
    kw = {'fields': [new_widget_id],
          'label_edit': new_widget_title,
         }

    widget = layout.manage_addCPSWidget(new_widget_id, new_widget_type, **kw)
    layoutdef = layout.getLayoutDefinition()
    layoutdef['rows'].append([{'ncols': 1, 'widget_id': new_widget_id}])

    if (metadata_schema is None 
        or not metadata_schema.has_key('f__' + new_widget_id)):
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

# And finally save the new layout
layout.setLayoutDefinition(layoutdef)

return RESPONSE.redirect('cpstypes_edit?type_id='+type_id)

