##parameters=fieldinfo, REQUEST, RESPONSE=None

action = None
for key in REQUEST.keys():
    if key.startswith('action_'):
        action = key[7:] # remove the 'action_'-part
        break
       
if not action:
    raise ValueError('No action specified')

schema = context.cpstypes_get_schema()

for info in fieldinfo:
    field = schema[info['id']]
    is_selected = info.get('is_selected',0)
    if action == 'delete' and is_selected:    
        schema.manage_delObjects([info['id']])
    else:
        if field.hasProperty('default_widget'):
            field.manage_changeProperties(default_widget = info['widget'])
        else:
            field.manage_addProperty('default_widget', info['widget'], 'string')

if RESPONSE:
    return RESPONSE.redirect(context.portal_url() + '/cpstypes_schema_edit')
else:
    return 'Updated'
