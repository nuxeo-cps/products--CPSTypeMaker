##parameters=type_id, widgetinfo=[], new_widget_title=None, new_widget_type=None, REQUEST=None, RESPONSE=None

from Products.CPSCore.utils import makeId

action = None
for key in REQUEST.keys():
    if key.startswith('action_'):
        action = key[7:] # remove the 'action_'-part
        break
       
if not action:
    raise ValueError('No action specified')

defs = context.cpstypes_get_definitions()
type_prefix = defs['type_prefix']
flex_id = type_prefix + 'flexible_' + type_id[len(type_prefix):]
layout = context.portal_layouts[flex_id]
typeob = context.portal_types[type_id]
portal_status_message = []

new_widget_id = makeId(new_widget_title)
flexible_widgets = []

for each in widgetinfo:
    widgetname = each['name']
    widgetid = each['id']
    widget_repeats = each.get('repeats')
    
    is_selected = each.get('is_selected',0)
    widget = layout[widgetid]
    
    if action == 'delete' and is_selected:    
        layout.manage_delObjects([widgetid])
    else:
        # Update widget data
        kw = {'label_edit': each['title'],
              'title': each['title'],
              'size_max': each['size'],
             } 
        widget.manage_changeProperties(**kw)
        if widget_repeats and int(widget_repeats) > 0:
            winfo = widgetname + ':' + str(widget_repeats)
        else:
            winfo = widgetname
        flexible_widgets.append(winfo)
        

if action == 'add' and new_widget_id:
    kw = {'fields': ['?'],
          'label_edit': new_widget_title,
          'title': new_widget_title,
         }

    if hasattr(layout, 'w__'+new_widget_id):
        portal_status_message.append('field_already_exists')

    else:
        widget = layout.manage_addCPSWidget(new_widget_id, new_widget_type, **kw)
        flexible_widgets.append(new_widget_id)

layout.manage_changeProperties(flexible_widgets=flexible_widgets)
if flexible_widgets:
    typeob.manage_changeProperties(flexible_layouts=flex_id + ':' + flex_id)
else:
    typeob.manage_changeProperties(flexible_layouts='')

if portal_status_message:
    portal_status_message = '\n'.join(portal_status_message)
    portal_status_message = '&portal_status_message=' + portal_status_message
else:
    portal_status_message = ''

return RESPONSE.redirect('cpstypes_edit_flexible?type_id='+type_id+portal_status_message)
    
