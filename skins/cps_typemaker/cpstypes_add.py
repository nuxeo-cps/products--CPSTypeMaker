##parameters=id,title,description,RESPONSE=None

ttool = context.portal_types
defs = context.cpstypes_get_definitions()
prefix = defs['type_prefix']
workspace_wf = defs['workspace_wf']
section_wf = defs['section_wf']
workspaceid = defs['workspaceid']
sectionid = defs['sectionid']
schemaid = defs['schemaid']

type_id = prefix + id
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
    'schemas': [schemaid],
    'layouts': [type_id],
    }
ti.manage_changeProperties(**properties)

ltool = context.portal_layouts
layout = ltool.manage_addCPSLayout(type_id)
layout.manage_changeProperties(style_prefix='layout_default_')


for type in ('Workspace', 'Section'):
    typeobj = ttool[type]
    workspaceACT = list(typeobj.allowed_content_types)
    if type_id not in  workspaceACT:
        workspaceACT.append(type_id)
        typeobj.manage_changeProperties(allowed_content_types = workspaceACT)


portal = context.portal_url.getPortalObject()
wfconf = getattr(portal[sectionid], '.cps_workflow_configuration')
if not wfconf.getPlacefulChainFor(type_id):
    wfconf.manage_addChain(portal_type=type_id, chain=section_wf)

wfconf = getattr(portal[workspaceid], '.cps_workflow_configuration')
if not wfconf.getPlacefulChainFor(type_id):
    wfconf.manage_addChain(portal_type=type_id, chain=workspace_wf)

if RESPONSE:
    return RESPONSE.redirect(context.portal_url() + '/cpstypes_edit?type_id='+type_id)
else:
    return 'Updated'
