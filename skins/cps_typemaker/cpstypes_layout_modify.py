##parameters=REQUEST, RESPONSE, type_id

layout = context.portal_layouts[type_id]
kw = {}
kw.update(REQUEST.form)
layout.manage_changeLayout( **kw)

RESPONSE.redirect(context.portal_url()+'/cpstypes_layout_edit?type_id='+type_id)
