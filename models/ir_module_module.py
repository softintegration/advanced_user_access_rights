# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
from odoo.release import series
from odoo.tools import parse_version


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def write(self, values):
        """
        When new module is installed or existing one is updated we have to clear the _refresh_model_methods cache as new or updated module can add new
        methods to existing models that have been already added in access right rules by methods
        """
        res = super(IrModuleModule,self).write(values)
        self.env['ir.model.method.access']._refresh_model_methods.clear_cache(self)
        return res
