##parameters=mode,datastructure


if datastructure.has_key('vocabulary'):
    value = datastructure['vocabulary']
else:
    value = None


#raise str(datastructure)

if mode == 'edit':

    structured_result = '<select name="widget__vocabulary">\n'

    # see if we want to see ALL vocab types
    #for vocab in context.portal_vocabularies.objectValues('CPS Vocabulary'):
    for vocab in context.portal_vocabularies.objectValues():

        structured_result += '<option value="'
        structured_result += vocab.id
        structured_result += '"'
        if (value is not None) and (value == vocab.id):
            structured_result += ' selected="selected" '
        structured_result += '>\n'
        structured_result += vocab.id
        structured_result += '</option>\n'

    structured_result += '</select>\n'

# default mode : the view mode
else:

    if value is not None:
        structured_result = str(value)
    else:
        structured_result = ''

return structured_result