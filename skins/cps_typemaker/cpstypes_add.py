##parameters=id,title,description

ttool = context.portal_types
defs = context.cpstypes_get_definitions()
prefix = defs['type_prefix']
workspace_wf = defs['workspace_wf']
section_wf = defs['section_wf']


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
    'schemas': ['metadata'],
    'layouts': [type_id],
    'cps_section_wf': 'section_content_wf',
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
section_wf = getattr(portal['sections'], '.cps_workflow_configuration')
if not section_wf.getPlacefulChainFor(type_id):
    section_wf.manage_addChain(portal_type=type_id, chain=section_wf)

workspace_wf = getattr(portal['workspaces'], '.cps_workflow_configuration')
if not workspace_wf.getPlacefulChainFor(type_id):
    workspace_wf.manage_addChain(portal_type=type_id, chain=workspace_wf)

return context.cpstypes_view(type_id=type_id)
