##parameters=layout_id, new_field, RESPONSE=None

ltool = context.portal_layouts
layout = ltool[layout_id]

kw = {'fields': [new_field],
      'label': new_field,
      'label_edit': new_field,
     }

field = context.cpstypes_get_schema()[new_field]
wtype = field.default_widget

layout.manage_addCPSWidget(new_field, wtype, **kw)
layoutdef = layout.getLayoutDefinition()
layoutdef['rows'].append([{'ncols': 1, 'widget_id': new_field}])
layout.setLayoutDefinition(layoutdef)

if RESPONSE:
    return RESPONSE.redirect(context.portal_url() + '/cpstypes_edit?type_id='+layout_id)
else:
    return 'Updated'
