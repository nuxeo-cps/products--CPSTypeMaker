##parameters=mode,datastructure

if datastructure.has_key('directory'):
    value = datastructure['directory']
else:
    value = None



if mode == 'edit':
    structured_result = '<select name="widget__directory">\n'

    # empty option
    structured_result += '<option value=""'
    if (value is not None) and (value == ""):
            structured_result += ' selected="selected" '
    structured_result += '>'

    structured_result += '</option>'

    for directory_id, directory in context.portal_directories.objectItems():

        # XXX see if we want to filter here
        if directory.isVisible():
            structured_result += '<option value="'
            structured_result += directory_id
            structured_result += '"'
            if (value is not None) and (value == directory_id):
                structured_result += ' selected="selected" '
            structured_result += '>\n'


            if directory.title <> '':
                structured_result += directory.title
            else:
                structured_result += directory_id


            structured_result += '</option>\n'

    structured_result += '</select>\n'

# default mode : the view mode
else:
    if value is not None:
        structured_result = str(value)
    else:
        structured_result = ''

return structured_result