##parameters=

schema_id  = context.cpstypes_get_definitions()['schemaid']
stool = context.portal_schemas
if hasattr(stool, schema_id):
    return getattr(stool, schema_id)
    
return stool.manage_addCPSSchema(schema_id)

