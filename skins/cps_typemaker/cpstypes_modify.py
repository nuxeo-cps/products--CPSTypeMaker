##parameters=REQUEST, RESPONSE

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

# Firstly, save any changes to the fields.
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
    
