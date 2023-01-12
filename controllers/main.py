# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo.addons.web.controllers.main import Export,ExcelExport,CSVExport,serialize_exception
from odoo.http import request
from odoo import http,SUPERUSER_ID,_
from odoo.exceptions import ValidationError


class ExportInherit(Export):

    @http.route('/web/export/get_fields', type='json', auth="user")
    def get_fields(self, model, prefix='', parent_name='',
                   import_compat=True, parent_field_type=None,
                   parent_field=None, exclude=None):
        # here we have to add our layer of security
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        user = request.env.user
        if user.id in (SUPERUSER_ID, request.env.ref('base.user_admin').id):
            return super(ExportInherit,self).get_fields(model,prefix=prefix,parent_name=parent_name,import_compat=import_compat,
                                                    parent_field_type=parent_field_type,parent_field=parent_field,
                                                    exclude=exclude)
        # if no access rules has been configured for this model ,nothing will be done
        if not user._model_has_access_rules(model):
            return super(ExportInherit,self).get_fields(model,prefix=prefix,parent_name=parent_name,import_compat=import_compat,
                                                    parent_field_type=parent_field_type,parent_field=parent_field,
                                                    exclude=exclude)
        if not user._has_permission(model, 'export'):
            raise ValidationError(_("You have not necessary access right to do this action,please contact system administrator!"))
        return super(ExportInherit,self).get_fields(model,prefix=prefix,parent_name=parent_name,import_compat=import_compat,
                                                    parent_field_type=parent_field_type,parent_field=parent_field,
                                                    exclude=exclude)


class ExcelExportInherit(ExcelExport):

    @http.route('/web/export/xlsx', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        # here we have to add our layer of security
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        user = request.env.user
        if user.id in (SUPERUSER_ID, request.env.ref('base.user_admin').id):
            return super(ExcelExportInherit,self).index(data)
        # if no access rules has been configured for this model ,nothing will be done
        data_parsed = json.loads(data)
        if not user._model_has_access_rules(data_parsed["model"]):
            return super(ExcelExportInherit,self).index(data)
        if not user._has_permission(data_parsed["model"], 'export'):
            raise ValidationError(
                _("You have not necessary access right to do this action,please contact system administrator!"))
        return super(ExcelExportInherit,self).index(data)


class CSVExportInherit(CSVExport):

    @http.route('/web/export/csv', type='http', auth="user")
    @serialize_exception
    def index(self, data):
        # here we have to add our layer of security
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        user = request.env.user
        if user.id in (SUPERUSER_ID, request.env.ref('base.user_admin').id):
            return super(CSVExportInherit, self).index(data)
        # if no access rules has been configured for this model ,nothing will be done
        data_parsed = json.loads(data)
        if not user._model_has_access_rules(data_parsed["model"]):
            return super(CSVExportInherit, self).index(data)
        if not user._has_permission(data_parsed["model"], 'export'):
            raise ValidationError(
                _("You have not necessary access right to do this action,please contact system administrator!"))
        return super(CSVExportInherit, self).index(data)