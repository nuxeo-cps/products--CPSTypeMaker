##parameters=field_type=None

mapping = { 'CPS String List Field': ('MultiSelect Widget', 'Lines Widget', 
                'Ordered List Widget', 'Unordered List Widget'),
            'CPS String Field': ('String Widget', 'TextArea Widget', 
                'Email Widget', 'Heading Widget', 'Rich Text Editor Widget',
                'InternalLinks Widget', 'Link Widget', 'Html Widget'),
            'CPS DateTime Field': ('DateTime Widget', 'Date Widget'),
            'CPS Password Field': ('Password Widget',),
            'CPS Int Field': ('Int Widget', 'CheckBox Widget'),
            'CPS Long Field': ('Long Widget',),
            'CPS Float Field': ('Float Widget',),
            'CPS File Field': ('AttachedFile Widget', ' File Widget'),
            'CPS Image Field': ('Image Widget', 'Photo Widget'),
          }

if field_type:
    return mapping[field_type]

return mapping.keys()