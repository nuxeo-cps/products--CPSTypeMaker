##parameters=type_id, title, description, icon, is_flexible=None, REQUEST=None, RESPONSE=None

action = None
for key in REQUEST.keys():
    if key.startswith('action_'):
        action = key[7:] # remove the 'action_'-part
        break
       
if not action:
    raise ValueError('No action specified')

layoutid = REQUEST['type_id']
layout = context.portal_layouts[layoutid]
layoutdef = layout.getLayoutDefinition()
defs = context.cpstypes_get_definitions()
flexible_layout = defs['flexible_layout']
flexible_schema = defs['flexible_schema']

ttool = context.portal_types
type = ttool[type_id]

props = {}
for id, value in type.propertyItems():
    props[id] = value

#raise str(props)
layouts = props['layouts']
schemas = props['schemas']
if is_flexible:
    if not flexible_layout in layouts:
        layouts.append(flexible_layout)
    if not flexible_schema in schemas:
        schemas.append(flexible_schema)
    props['flexible_layouts'] = [flexible_layout + ':' + flexible_schema]
else:
    if flexible_layout in layouts:
        layouts.remove(flexible_layout)
    if flexible_schema in schemas:
        schemas.remove(flexible_schema)
    props['flexible_layout'] = []

props['layouts'] = layouts
props['schemas'] = schemas
props['title'] = title
props['description'] = description
props['content_icon'] = icon

type.manage_changeProperties(**props)

widgetinfo = REQUEST.get('widgetinfo', [])

for each in widgetinfo:
    widgetname = each['name']
    widgetid = each['id']
    is_selected = each.get('is_selected',0)
    
    if action == 'delete' and is_selected:    
        layout.manage_delObjects([widgetid])
        new_rows = []
        for row in layoutdef['rows']:
            new_widgets = []
            for widget in row:
                if widget['widget_id'] != widgetname:
                    new_widgets.append(widget)
            if new_widgets:
                new_rows.append(row)
        layoutdef['rows'] = new_rows
    else:
        widget = layout[each['name']]
        widget.manage_changeProperties(label=each['title'], label_edit=each['title'],
            is_required=each.get('required',0), size_max=each['size'])

if action in ('delete',):       
    layout.setLayoutDefinition(layoutdef)

return RESPONSE.redirect('cpstypes_edit?type_id='+layoutid)
    
