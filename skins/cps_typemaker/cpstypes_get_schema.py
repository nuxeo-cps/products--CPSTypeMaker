##parameters=

schema_id  = context.cpstypes_get_definitions()['schemaid']
stool = context.portal_schemas
if hasattr(stool, schema_id):
    return getattr(stool, schema_id)
    
schema = stool.manage_addCPSSchema(schema_id)
schema.manage_addField('Title', 'CPS String Field')
schema.manage_addField('Description', 'CPS String Field')
return schema