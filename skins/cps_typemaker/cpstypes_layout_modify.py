##parameters=REQUEST, RESPONSE, type_id
from urllib import quote, urlencode, unquote
from cgi import escape

layout = context.portal_layouts[type_id]
kw = {}
kw.update(REQUEST.form)

used_widgets = []
duplicate_widgets = []
row = 1
while kw.has_key('cell_%d_1' % row):
    cell = 1
    while kw.has_key('cell_%d_%d' % (row, cell)):
        widget_id = kw.get('cell_%d_%d' % (row, cell), '')
        if widget_id in used_widgets and not (kw.has_key('delcell') and \
           kw.get('check_%d_%d' % (row, cell))):
            duplicate_widgets.append(widget_id)
            kw['cell_%d_%d' % (row, cell)] = ''
        else:
            used_widgets.append(widget_id)
        cell += 1
    row += 1
     
layout.manage_changeLayout(**kw)

mcat = context.Localizer.default
if duplicate_widgets:
    message = quote(mcat('psm_duplicate_widgets') + ', '.join(duplicate_widgets))
else:
    message = 'psm_changed'

RESPONSE.redirect(
    context.portal_url()+
        '/cpstypes_layout_edit?type_id=%s&portal_status_message=%s' % (
        type_id, message))

