# -*- coding: utf-8 -*-


from lxml import etree
from odoo import models,fields,_,api
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)


class IrUiViewAccess(models.Model):
    _name = 'ir.ui.view.access'
    _description = 'View Access'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer(string='Sequence',
                              help="Gives the sequence order when displaying a list of access rules")
    active = fields.Boolean(default=True, help='If you uncheck the active field, it will disable the Rule without deleting it.')
    model_ids = fields.Many2many('ir.model','ir_ui_view_access_models','access_id','model_id',string='Models', required=True, index=True, ondelete='cascade')
    user_ids = fields.Many2many('res.users','ir_ui_view_access_users','access_id','user_id', string='Users', required=True,ondelete='restrict', index=True,)
    perm_read = fields.Boolean(string='Read', default=True)
    perm_write = fields.Boolean(string='Write', default=True)
    perm_create = fields.Boolean(string='Create', default=True)
    perm_delete = fields.Boolean(string='Delete', default=True)
    perm_print = fields.Boolean(string='Print', default=True)
    perm_export = fields.Boolean(string='Export', default=True)


    # we have to deal with cache in the case of update or delete
    # it is important to note that the clearing of the cache must be doing after the calling of the ORM super method,
    # this is for the sake of the performance because if we clearing the cache before calling the ORM method,we can fall into
    # the situation where the cache is invalidated without any reason (because the ORM method raising error)
    # FIXME: for the sake of performance we have to clear cache only in the case of :
    # FIXME: create : if perm_print or perm_write are False
    # FIXME: write : if perm_print or perm_create are modified
    # FIXME: unlink: we have to clear cache without checking in this case

    @api.model
    def create(self, vals):
        res = super(IrUiViewAccess, self).create(vals)
        self.env['ir.actions.actions']._get_bindings.clear_cache(self)
        return res

    def write(self, vals):
        res = super(IrUiViewAccess, self).write(vals)
        self.env['ir.actions.actions']._get_bindings.clear_cache(self)
        return res

    def unlink(self):
        res = super(IrUiViewAccess, self).unlink()
        self.env['ir.actions.actions']._get_bindings.clear_cache(self)
        return res



