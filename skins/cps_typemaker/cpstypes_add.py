##parameters=title,description,RESPONSE=None

from Products.CPSCore.utils import makeId

id = makeId(title)
ttool = context.portal_types
stool = context.portal_schemas
ltool = context.portal_layouts
defs = context.cpstypes_get_definitions()
prefix = defs['type_prefix']
base_layouts = defs['base_layouts']
base_schemas = defs['base_schemas']
add_in_types = defs['add_in_types']
style_prefix = defs['style_prefix']
type_actions = defs['type_actions']

type_id = prefix + id
flex_id = prefix + 'flexible_' + id

ti = ttool.addFlexibleTypeInformation(id=type_id)
properties = {
    'title': title,
    'description': description,
    'content_icon': 'document_icon.gif',
    'content_meta_type': 'CPS Document',
    'product': 'CPSDocument',
    'factory': 'addCPSDocument',
    'immediate_view': 'cpsdocument_view',
    'global_allow': 1,
    'filter_content_types': 1,
    'allowed_content_types': (),
    'allow_discussion': 0,
    'cps_is_searchable': 1,
    'cps_proxy_type': 'document',
    'schemas': base_schemas + [type_id, flex_id],
    'layouts': base_layouts + [type_id, flex_id],
    }
ti.manage_changeProperties(**properties)

if type_actions:
    ti.deleteActions(range(0, len(ti.listActions())))
    for action in type_actions:
        ti.addAction(**action)

layout = ltool.manage_addCPSLayout(type_id)
layout.manage_changeProperties(style_prefix=style_prefix)
flexlayout = ltool.manage_addCPSLayout(flex_id)
flexlayout.manage_changeProperties(style_prefix=style_prefix)

for type in add_in_types:
    typeobj = ttool[type]
    workspaceACT = list(typeobj.allowed_content_types)
    if type_id not in  workspaceACT:
        workspaceACT.append(type_id)
        typeobj.manage_changeProperties(allowed_content_types = workspaceACT)


portal = context.portal_url.getPortalObject()
for sectionspace, workflow in context.cpstypes_get_workflows().items():
    wfconf = getattr(portal[sectionspace], '.cps_workflow_configuration')
    if not wfconf.getPlacefulChainFor(type_id):
        wfconf.manage_addChain(portal_type=type_id, chain=workflow)

stool.manage_addCPSSchema(type_id)
stool.manage_addCPSSchema(flex_id)

if RESPONSE:
    return RESPONSE.redirect(context.portal_url() + '/cpstypes_edit?type_id='+type_id)
else:
    return 'Updated'
