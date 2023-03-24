# -*- coding: utf-8 -*-


import logging

from odoo import models

_logger = logging.getLogger(__name__)

MESSAGE_MODEL = 'mail.message'


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """ We have to use this method because it is the interface with the javascript code in web client"""
        res = super(Http, self).session_info()
        res.update({'can_edit_delete_message':self._can_edit_delete_message()})
        return res

    def _can_edit_delete_message(self):
        """ This method check the permission of edit and deletion of messages for the current user
        Note that the two permission are merged because in the context of messages ,the edit and delete represents
        the same permission"""
        return self.env.user._has_permission(MESSAGE_MODEL, 'write') and self.env.user._has_permission(MESSAGE_MODEL,
                                                                                                      'delete')
