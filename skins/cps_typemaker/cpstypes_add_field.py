##parameters=layout_id, new_field

ltool = context.portal_layouts
layout = ltool[layout_id]

kw = {'fields': [new_field],
      'label': new_field,
      'label_edit': new_field,
     }

layout.manage_addCPSWidget(new_field, 'String Widget', **kw)
layoutdef = layout.getLayoutDefinition()
layoutdef['rows'].append([{'ncols': 1, 'widget_id': new_field}])
layout.setLayoutDefinition(layoutdef)

return context.cpstypes_view(type_id=layout_id)