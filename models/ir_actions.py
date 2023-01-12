# -*- coding: utf-8 -*-


from lxml import etree
from odoo import api,models,fields,_,tools,SUPERUSER_ID
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)


class IrActions(models.Model):
    _inherit = 'ir.actions.actions'

    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'model_name', 'debug')
    def _get_bindings(self, model_name, debug=False):
        res = super(IrActions,self)._get_bindings(model_name,debug=debug)
        # here we have to add our layer of security
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        if self.env.user.id in (SUPERUSER_ID, self.env.ref('base.user_admin').id):
            return res
        # if no access rules has been configured for this model ,nothing will be done
        if not self.env.user._model_has_access_rules(model_name):
            return res
        if not self.env.user._has_permission(model_name, 'write'):
            if res.get('action',False):
                res['action'] = []
        if not self.env.user._has_permission(model_name, 'print'):
            if res.get('report',False):
                res['report'] = []
        return res
