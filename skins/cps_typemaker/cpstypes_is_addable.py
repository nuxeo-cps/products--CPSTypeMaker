##parameters=type_id

# Checkes is the type is allowed in any of the types it should be allowed in.
defs = context.cpstypes_get_definitions()
types = defs['add_in_types']
ttool = context.portal_types

for type in types:
    typeob = ttool[type]
    if type_id in typeob.allowed_content_types:
        return 1
        
return 0