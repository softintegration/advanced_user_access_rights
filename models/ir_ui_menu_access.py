# -*- coding: utf-8 -*-


from lxml import etree
from odoo import models,fields,_,api
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)


class IrUiMenuAccess(models.Model):
    _name = 'ir.ui.menu.access'
    _description = 'Menu Access'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "sequence"

    sequence = fields.Integer(string='Sequence',
                              help="Gives the sequence order when displaying a list of access rules")
    active = fields.Boolean(default=True, help='If you uncheck the active field, it will disable the Rule without deleting it.')
    menu_ids = fields.Many2many('ir.ui.menu','ir_ui_menu_access_menus','access_id','menu_id',string='Menu', required=True, index=True, ondelete='cascade')
    user_ids = fields.Many2many('res.users','ir_ui_menu_access_users','access_id','user_id', string='Users', required=True,ondelete='restrict', index=True,)
    visible = fields.Boolean(string='Visible')


    # we have to deal with cache in the case of update or delete
    # it is important to note that the clearing of the cache must be doing after the calling of the ORM super method,
    # this is for the sake of the performance because if we clearing the cache before calling the ORM method,we can fall into
    # the situation where the cache is invalidated without any reason (because the ORM method raising error)
    @api.model
    def create(self, vals):
        res = super(IrUiMenuAccess, self).create(vals)
        self.env['ir.ui.menu']._visible_menu_ids.clear_cache(self)
        return res

    def write(self, vals):
        res = super(IrUiMenuAccess, self).write(vals)
        self.env['ir.ui.menu']._visible_menu_ids.clear_cache(self)
        return res

    def unlink(self):
        res = super(IrUiMenuAccess, self).unlink()
        self.env['ir.ui.menu']._visible_menu_ids.clear_cache(self)
        return res