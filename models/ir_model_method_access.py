# -*- coding: utf-8 -*-


from lxml import etree
from odoo import models, fields, _, api,tools
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)

OPERATIONS_SEPARATOR = ","


class IrModelMethodAccess(models.Model):
    _name = 'ir.model.method.access'
    _description = 'Method access'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer(string='Sequence',
                              help="Gives the sequence order when displaying a list of access rules", index=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True, index=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', store=True, required=False)
    method_ids = fields.Many2many('ir.model.method', 'ir_model_method_access_method_rel', 'access_id', 'method_id',
                                 'Operation')
    user_ids = fields.Many2many('res.users','ir_model_method_access_users','access_id','user_id',  string='Users',
                                required=False, ondelete='restrict', index=True, )
    group_ids = fields.Many2many('res.groups','ir_model_method_access_groups','access_id','group_id', string='Groups', required=False,ondelete='restrict', index=True,)
    users_required = fields.Boolean(string='Users or groups required',help='If the users is required ,the groups are not')
    can_do = fields.Boolean(string='Has access', default=False)
    active = fields.Boolean(default=True,
                            help='If you uncheck the active field, it will disable the Rule without deleting it.')


    @api.model
    def create(self, vals):
        res = super(IrModelMethodAccess, self).create(vals)
        self.env['res.users']._has_method_permission.clear_cache(self)
        return res

    def write(self, vals):
        res = super(IrModelMethodAccess, self).write(vals)
        self.env['res.users']._has_method_permission.clear_cache(self)
        return res

    def unlink(self):
        res = super(IrModelMethodAccess, self).unlink()
        self.env['res.users']._has_method_permission.clear_cache(self)
        return res

    def refresh_model_methods(self):
        for each in self:
            each._refresh_model_methods(each.model_id)

    @tools.ormcache('model')
    def _refresh_model_methods(self,model):
        # FIXME:actually this method doesn't scale because it is of exponential time complexity O(2^n),but at this level of usage ,it is sufficient
        # FIXME:the solution is to find up only the new added methods without searching for all the object method every time
        methods_to_create = []
        for method_name in dir(self.env[model.model]):
            if not method_name.startswith('__') and not method_name.startswith('_') and callable(getattr(self.env[model.model], method_name)):
                if not self.env['ir.model.method'].search_count([('model_id','=',model.id),('method','=',method_name)]):
                    methods_to_create.append({'model_id':model.id,'method':method_name})
        self.env['ir.model.method'].create(methods_to_create)


    #@api.constrains('model_id','user_ids')
    #def _check_model_unicity(self):


class IrModelMethod(models.Model):
    _name = 'ir.model.method'
    _rec_name = 'method'

    model_id = fields.Many2one('ir.model', string='Model', required=True, index=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model', store=True, required=False)
    method = fields.Char(string='Method',required=True)

