# -*- coding: utf-8 -*-

{
    'name': 'Advanced user access rights',
    'version': '1.0.1',
    'author':'Soft-integration',
    'category': 'Security/Access rights',
    'description': "",
    'depends': [
        'portal'
    ],
    'data': [
        'security/advanced_user_access_rights_security.xml',
        'security/ir.model.access.csv',
        'views/ir_ui_menu_access_views.xml',
        'views/ir_ui_view_access_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
