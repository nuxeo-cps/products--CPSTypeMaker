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
    
if action == 'delete':
    selected = REQUEST.get('selected_ids', [])
    widgetnames = [layout[w].getWidgetId() for w in selected]
        
    layout.manage_delObjects(selected)
    layoutdef = layout.getLayoutDefinition()
    new_rows = []
    for row in layoutdef['rows']:
        new_widgets = []
        for widget in row:
            if widget['widget_id'] not in widgetnames:
                new_widgets.append(widget)
        if new_widgets:
            new_rows.append(row)
    layoutdef['rows'] = new_rows
    layout.setLayoutDefinition(layoutdef)

    
return RESPONSE.redirect('cpstypes_view?type_id='+layoutid)
    
