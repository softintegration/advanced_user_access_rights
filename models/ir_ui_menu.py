# -*- coding: utf-8 -*-


from lxml import etree
from odoo import api,models,fields,_,tools,SUPERUSER_ID
from odoo.addons.base.models.ir_ui_view import transfer_field_to_modifiers
import logging

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        visible_menu_ids = super(IrUiMenu, self)._visible_menu_ids(debug=debug)
        # The super-administrators (technical admin user and human admin user) are not concerned by this constrains
        if self.env.user.id in (SUPERUSER_ID,self.env.ref('base.user_admin').id):
            return visible_menu_ids
        forced_visible_menu_ids = self.env.user._visible_menus()
        for invisible_menu in self.env.user._invisible_menus().filtered(lambda menu:menu not in forced_visible_menu_ids):
            visible_menu_ids.remove(invisible_menu.id)
        return visible_menu_ids


