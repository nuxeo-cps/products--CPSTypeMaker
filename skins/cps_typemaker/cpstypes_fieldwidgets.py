##parameters=field_type=None

mapping = { 'CPS String List Field': ('MultiSelect Widget',),
            'CPS String Field': ('Text Widget', 'TextArea Widget', 'String Widget',),
            'CPS DateTime Field': ('DateTime Widget', 'Date Widget',),
          }

if field_type:
    return mapping[field_type]

return mapping.keys()