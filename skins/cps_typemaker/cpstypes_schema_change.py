##parameters=fieldinfo, REQUEST, RESPONSE=None

schema = context.portal_schemas.metadata

for info in fieldinfo:
    field = schema[info['id']]
    if field.hasProperty('default_widget'):
        field.manage_changeProperties(default_widget = info['widget'])
    else:
        field.manage_addProperty('default_widget', info['widget'], 'string')

if RESPONSE:
    return RESPONSE.redirect(context.portal_url() + '/cpstypes_schema_edit')
else:
    return updated
