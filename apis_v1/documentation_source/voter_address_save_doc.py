# apis_v1/documentation_source/voter_address_save_doc.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-


def voter_address_save_doc_template_values(url_root):
    """
    Show documentation about voterAddressSave
    """
    required_query_parameter_list = [
        {
            'name':         'voter_device_id',
            'value':        'string',  # boolean, integer, long, string
            'description':  'An 88 character unique identifier (from cookie - not URL variable) linked to '
                            'a voter record on the server',
        },
        {
            'name':         'address',
            'value':        'string',  # boolean, integer, long, string
            'description':  'The address text a voter enters to identify the location tied to their ballot. '
                            '(Not mailing address.)',
        },
    ]
    optional_query_parameter_list = [
        # {
        #     'name':         '',
        #     'value':        '',  # boolean, integer, long, string
        #     'description':  '',
        # },
    ]

    api_response = '{\n' \
                   '  "status": string (description of what happened),\n' \
                   '  "voter_device_id": string (88 characters long),\n' \
                   '  "address": string (the value just saved),\n' \
                   '  "success": boolean (did the save happen?),\n' \
                   '}'

    potential_status_codes_list = [
        {
            'code':         'VALID_VOTER_DEVICE_ID_MISSING',
            'description':  'Cannot proceed. A valid voter_device_id parameter was not included.',
        },
        {
            'code':         'MISSING_VOTER_ID_OR_ADDRESS_TYPE',
            'description':  'Cannot proceed. Missing variables voter_id or address_type while trying to save.',
        },
        {
            'code':         'VOTER_ADDRESS_SAVED',
            'description':  'Successfully saved',
        },
        {
            'code':         'MULTIPLE_MATCHING_ADDRESSES_FOUND',
            'description':  'Could not save. Multiple entries already saved.',
        },
        {
            'code':         'MISSING_POST_VARIABLE-ADDRESS',
            'description':  'Could not save. POST variable \'address\' is required.',
        },
    ]

    template_values = {
        'api_name': 'voterAddressSave',
        'api_slug': 'voterAddressSave',
        'api_introduction':
            "Save or create an address for the current voter.",
        'try_now_link': 'apis_v1:voterAddressSaveView',
        'try_now_link_variables': '',
        'url_root': url_root,
        'get_or_post': 'POST',
        'required_query_parameter_list': required_query_parameter_list,
        'optional_query_parameter_list': optional_query_parameter_list,
        'api_response': api_response,
        'api_response_notes':
            "",
        'potential_status_codes_list': potential_status_codes_list,
    }
    return template_values
