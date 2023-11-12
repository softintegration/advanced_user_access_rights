# -*- coding: utf-8 -*-


from lxml import etree
from odoo import api,models,fields,_,tools
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging
import psycopg2

_logger = logging.getLogger(__name__)

def _check_table_existence(cr,tables):
    for table in tables:
        sql = "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = '%s') AS table_existence;"%table
        cr.execute(sql)
        exist = cr.fetchone()[0]
        if not exist:
            return False
    return True


class Users(models.Model):
    _inherit = "res.users"

    menu_access_rules_count = fields.Integer("Count of configured access menus", compute='_compute_menu_access_rules_count')
    view_access_rules_count = fields.Integer("Count of configured access views", compute='_compute_view_access_rules_count')
    method_access_rules_count = fields.Integer("Count of configured access methods", compute='_compute_method_access_rules_count')

    def _compute_menu_access_rules_count(self):
        for each in self:
            each.menu_access_rules_count = len(each._get_menu_access_rules())

    def _compute_view_access_rules_count(self):
        for each in self:
            each.view_access_rules_count = len(each._get_view_access_rules())

    def _compute_method_access_rules_count(self):
        for each in self:
            each.method_access_rules_count = len(each._get_method_access_rules())

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

    def action_view_method_access_rules(self):
        return {
            'res_model': 'ir.model.method.access',
            'type': 'ir.actions.act_window',
            'name': _("Operations access rule"),
            'domain': [('id', 'in', self._get_method_access_rules().ids)],
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

    def _get_method_access_rules(self,model_id=False):
        domain = self._get_method_access_rules_domain()
        if model_id:
            domain.append(('model_ids','in',model_id))
        method_access_rules = self.env['ir.model.method.access'].search(domain)
        return method_access_rules

    def _get_view_access_rules_domain(self):
        domain = ['|',('user_ids', 'in', self.id),('group_ids','in',self.groups_id.ids)]
        return domain

    def _get_method_access_rules_domain(self):
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

    @tools.ormcache('self.id')
    def _check_table_existence(self,tables):
        for table in tables:
            sql = "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = '%s') AS table_existence;" % table
            self.env.cr.execute(sql)
            exist = self.env.cr.fetchone()[0]
            if not exist:
                return False
        return True

    @tools.ormcache('self','model','method')
    def _has_method_permission(self,model,method=False):
        domain = [('model_name', '=', model)]
        if method:
            domain.append(('method', '=', method))
        # if the feature has not been added yet we return True so that the behaviour remain the same
        if not self._check_table_existence([self.env['ir.model.method']._table]):
            return True
        method_to_check = self.env['ir.model.method'].search(domain, limit=1)
        if not method_to_check:
            return True
        sql = "SELECT id FROM ir_model_method_access imma " \
              "INNER JOIN ir_model_method_access_users immau ON imma.id = immau.access_id " \
              "INNER JOIN ir_model_method_access_method_rel immam ON imma.id = immam.access_id " \
              "WHERE immam.method_id = %s " \
              "AND   immau.user_id = %s " \
              "AND   imma.can_do = false " \
              "AND   imma.active = true LIMIT 1;"
        params = (tuple(method_to_check.ids),tuple(self.ids),)
        self.env.cr.execute(sql,params)
        access_ids = self._cr.fetchall()
        # if no method access rules has been added we consider all methods are allowed (treated by the upper security layer)
        if not access_ids:
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