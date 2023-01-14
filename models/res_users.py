# -*- coding: utf-8 -*-


from lxml import etree
from odoo import api,models,fields,_
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    menu_access_rules_count = fields.Integer("Count of configured access menus", compute='_compute_menu_access_rules_count')
    view_access_rules_count = fields.Integer("Count of configured access views", compute='_compute_view_access_rules_count')

    def _compute_menu_access_rules_count(self):
        for each in self:
            each.menu_access_rules_count = len(each._get_menu_access_rules())

    def _compute_view_access_rules_count(self):
        for each in self:
            each.view_access_rules_count = len(each._get_view_access_rules())

    def action_view_menu_access_rules(self):
        return {
            'res_model': 'ir.ui.menu.access',
            'type': 'ir.actions.act_window',
            'name': _("Menu access rule"),
            'domain': [('id', 'in', self._get_menu_access_rules().ids)],
            'context':{'default_user_ids':self.ids,
                       'readonly_users':True,
                       'default_users_required':True},
            'view_mode': 'tree',
        }

    def action_view_view_access_rules(self):
        return {
            'res_model': 'ir.ui.view.access',
            'type': 'ir.actions.act_window',
            'name': _("View access rule"),
            'domain': [('id', 'in', self._get_view_access_rules().ids)],
            'context':{'default_user_ids':self.ids,
                       'readonly_users':True,
                       'default_users_required':True},
            'view_mode': 'tree',
        }

    def _visible_menus(self):
        domain = self._visible_menus_domain()
        visible_menus = self.env['ir.ui.menu.access'].search(domain).mapped("menu_ids")
        return visible_menus

    def _visible_menus_domain(self):
        domain = self._get_menu_access_rules_domain()
        domain.append(('visible','=',True))
        return domain

    def _invisible_menus(self):
        domain = self._invisible_menus_domain()
        invisible_menus = self.env['ir.ui.menu.access'].search(domain).mapped("menu_ids")
        return invisible_menus

    def _invisible_menus_domain(self):
        domain = self._get_menu_access_rules_domain()
        domain.append(('visible','=',False))
        return domain

    def _get_menu_access_rules(self):
        domain = self._get_menu_access_rules_domain()
        menu_access_rules = self.env['ir.ui.menu.access'].search(domain)
        return menu_access_rules

    def _get_menu_access_rules_domain(self):
        domain = ['|',('user_ids', 'in', self.id),('group_ids','in',self.groups_id.ids)]
        return domain

    def _get_view_access_rules(self,model_id=False):
        domain = self._get_view_access_rules_domain()
        if model_id:
            domain.append(('model_ids','in',model_id))
        view_access_rules = self.env['ir.ui.view.access'].search(domain)
        return view_access_rules

    def _get_view_access_rules_domain(self):
        domain = ['|',('user_ids', 'in', self.id),('group_ids','in',self.groups_id.ids)]
        return domain

    def _model_has_access_rules(self,model):
        model = self.env['ir.model'].search([('model','=',model)])
        return len(self._get_view_access_rules(model_id=model.id)) > 0

    def _has_permission(self,model,perm):
        model = self.env['ir.model'].search([('model','=',model)])
        model_permissions = self._get_view_access_rules(model_id=model.id)
        for model_perm in model_permissions:
            if getattr(model_perm,'perm_%s'%perm):
                return True
        return False


class Groups(models.Model):
    _inherit = "res.groups"

    menu_access_rules_count = fields.Integer("Count of configured access menus",
                                             compute='_compute_menu_access_rules_count')
    view_access_rules_count = fields.Integer("Count of configured access views",
                                             compute='_compute_view_access_rules_count')

    def _compute_menu_access_rules_count(self):
        for each in self:
            each.menu_access_rules_count = len(each._get_menu_access_rules())

    def _compute_view_access_rules_count(self):
        for each in self:
            each.view_access_rules_count = len(each._get_view_access_rules())


    def _get_menu_access_rules(self):
        domain = self._get_menu_access_rules_domain()
        menu_access_rules = self.env['ir.ui.menu.access'].search(domain)
        return menu_access_rules

    def _get_menu_access_rules_domain(self):
        domain = [('group_ids', 'in', self.id)]
        return domain


    def action_view_menu_access_rules(self):
        return {
            'res_model': 'ir.ui.menu.access',
            'type': 'ir.actions.act_window',
            'name': _("Menu access rule"),
            'domain': [('id', 'in', self._get_menu_access_rules().ids)],
            'context':{'default_group_ids':self.ids,
                       'readonly_groups':True,
                       'default_users_required':False},
            'view_mode': 'tree',
        }


    def _get_view_access_rules(self,model_id=False):
        domain = self._get_view_access_rules_domain()
        if model_id:
            domain.append(('model_ids','in',model_id))
        view_access_rules = self.env['ir.ui.view.access'].search(domain)
        return view_access_rules

    def _get_view_access_rules_domain(self):
        domain = [('group_ids', 'in', self.id)]
        return domain

    def action_view_view_access_rules(self):
        return {
            'res_model': 'ir.ui.view.access',
            'type': 'ir.actions.act_window',
            'name': _("View access rule"),
            'domain': [('id', 'in', self._get_view_access_rules().ids)],
            'context':{'default_group_ids':self.ids,
                       'readonly_groups':True,
                       'default_users_required':False},
            'view_mode': 'tree',
        }