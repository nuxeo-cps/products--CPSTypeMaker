##parameters=new_field_id, new_field_type, RESPONSE=None
if not new_field_id:
    raise ValueError('No ID given')
    
defs = context.cpstypes_get_definitions()
schemaid = defs['schemaid']
schema = context.portal_schemas[schemaid]
schema.manage_addField(new_field_id, new_field_type)
field = schema[new_field_id]
widgettype = context.cpstypes_fieldwidgets(new_field_type)[0]['id']
field.manage_addProperty('default_widget', widgettype, 'string')

if RESPONSE:
    return RESPONSE.redirect(context.portal_url() + '/cpstypes_schema_edit')
else:
    return 'Updated'
