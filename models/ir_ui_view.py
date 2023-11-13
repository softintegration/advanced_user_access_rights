# -*- coding: utf-8 -*-


from lxml import etree
from odoo import models, SUPERUSER_ID, api
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _postprocess_access_rights(self, node, model):
        super(IrUiView, self)._postprocess_access_rights(node, model)
        # here we have to add our layer of security
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        if self.env.user.id in (SUPERUSER_ID, self.env.ref('base.user_admin').id):
            return
        # if no access rules has been configured for this model ,nothing will be done
        if not self.env.user._model_has_access_rules(model._name):
            return
        if node.tag in ('form', 'tree', 'graph', 'kanban', 'calendar'):
            if not self.env.user._has_permission(model._name, 'create'):
                node.set('create', "0")
            if not self.env.user._has_permission(model._name, 'write'):
                node.set('edit', "0")
                node.set("multi_edit", "0")
            if not self.env.user._has_permission(model._name, 'delete'):
                node.set('delete', "0")
            if not self.env.user._has_permission(model._name, 'export'):
                node.set('export_xlsx', "0")
                node.set('export', "0")

    def _apply_groups(self, node, name_manager, node_info):
        super(IrUiView, self)._apply_groups(node, name_manager, node_info)
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        if self.env.user.id in (SUPERUSER_ID, self.env.ref('base.user_admin').id):
            return
        if node.tag in ('button',):
            if self.env.user._model_has_access_rules(name_manager.model._name) and \
                    not self.env.user._has_permission(name_manager.model._name, 'write') and not self._is_smart_button(node):
                node.set('invisible', "1")
            if not self.env.user._has_method_permission(name_manager.model._name, method=node.get('name')):
                node.set('invisible', "1")

    def _postprocess_tag_field(self, node, name_manager, node_info):
        super(IrUiView, self)._postprocess_tag_field(node, name_manager, node_info)
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        if self.env.user.id in (SUPERUSER_ID, self.env.ref('base.user_admin').id):
            return
        if node.get('name'):
            field = name_manager.model._fields.get(node.get('name'))
            if field and field.type in ('many2one', 'many2many'):
                comodel = self.env[field.comodel_name].sudo(False)
                # if no access rules has been configured for this model ,nothing will be done
                if not self.env.user._model_has_access_rules(comodel._name):
                    return
                can_create = self.env.user._has_permission(comodel._name, 'create')
                can_write = self.env.user._has_permission(comodel._name, 'write')
                # we have to force the restriction only in the case of prevent creation/edition,this is because if we force
                # the possibility of creation/edition in the case of true we will overwrite the restrictions imposed by upper security layers
                if not can_create:
                    node.set('can_create', 'false')
                if not can_write:
                    node.set('can_write', 'false')
            if not self.env.user._model_has_access_rules(name_manager.model._name):
                return
            if not self.env.user._has_permission(name_manager.model._name, 'write'):
                node_info['modifiers'].update({'readonly': True})

    @api.model
    def _is_smart_button(self, node):
        return node.get('class', False) == 'oe_stat_button'


