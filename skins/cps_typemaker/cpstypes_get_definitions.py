##parameters = 

# The widget_list and flexible_widget_list are simple lists of widget Ids, like this:
# listed_widgets = ['ExtendedSelect Widget',
#                   'Float Widget',
#                   'TextArea Widget',
#                   'Unordered List Widget',
#                   'Boolean Widget',
#                   'AttachedFile Widget',
#                   'String Widget',
#                   'Link Widget',
#                   'Date Widget',
#                   'Email Widget',
#                   'CheckBox Widget',
#                  ]
# Setting them to None (default) will display all widgets.

# type_actions is a list or tuple of action property dictionaries.
# type_actions = (
#         {'id': 'view',
#          'name': 'action_view',
#          'action': 'string:${object_url}/cpsdocument_view',
#          'condition': '',
#          'permission': ('View',),
#          'category': 'object',
#          'visible': 1,},
#         {'id': 'new_content',
#          'name': 'action_new_content',
#          'action': 'string:${object_url}/folder_factories',
#          'condition': "python:object.getTypeInfo().cps_proxy_type != 'document'",
#          'permission': ('Modify portal content',),
#          'category': 'object',
#          'visible': 1,},
#    )
# If specified, this will *replace* the default CPSDocument actions when the
# type is created. Set to None (or any false value) the default CPSDocument 
# actions will be used

# The 'metadata' schema is handled specially by CPSDocument, and should not 
# be edited. Therefore we need support for two metadata schemas. These are
# defined by 'metadata_schemas', and are typically either 'metadata' plus 
# another, or only the other. Only 'metadata' does not work, and more than 
# one other than 'metadata' makes no sense. 

return {'type_prefix': 'simpletype_', # The id prefix for TypeMaker types.
        'style_prefix': 'layout_default_tab_',
        'base_schemas': ['metadata', 'common'],
        'base_layouts': ['common'],
        'add_in_types': ['Workspace', 'Section'],
        'metadata_layout': 'metadata',
        'metadata_schemas': ['metadata', 'common'],
        'widget_list': None,
        'flexible_widget_list': None,
        'type_actions': None,
       }       