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
                 
return {'type_prefix': 'simpletype_', # The id prefix for TypeMaker types.
        'style_prefix': 'layout_default_tab_',
        'base_schemas': ['metadata', 'custom_metadata', 'common'],
        'base_layouts': ['common'],
        'add_in_types': ['Workspace', 'Section'],
        'metadata_id': 'custom_metadata',
        'widget_list': None,
        'flexible_widget_list': None,
       }