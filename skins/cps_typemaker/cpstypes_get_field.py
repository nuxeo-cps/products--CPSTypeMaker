##parameters=schema, widget
# Returns the field object associated with a widget. 

defs = context.cpstypes_get_definitions()
fieldid = widget.fields[0]
schemas = [schema] + defs['metadata_schemas']

for schemaid in schemas:
    schemaob = context.portal_schemas[schemaid]
    if schemaob.has_key(fieldid):
        return schemaob[fieldid]
        
raise AttributeError("Field %s is not found for widget %s in type %s" % (
        fieldid, widget.getId(), schema))