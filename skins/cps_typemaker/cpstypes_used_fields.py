##parameters=

prefix = context.cpstypes_get_definitions()['type_prefix']
ltool = context.portal_layouts
used_fields = []

for id in ltool.objectIds():
    if not id.startswith(prefix):
        continue
    layout = ltool[id]
    for widget in layout.objectValues():
        used_fields.extend(widget.fields)
        
return used_fields
    
