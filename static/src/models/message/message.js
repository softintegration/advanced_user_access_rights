/** @odoo-module **/


import { registerInstancePatchModel } from '@mail/model/model_core';
import { session } from '@web/session';

registerInstancePatchModel('mail.message', 'advanced_user_access_rights/static/src/models/message/message.js', {
    /**
     * @override
     */
    _computeCanBeDeleted() {
         if (!session.can_edit_delete_message) {
                return false;
         }
        return this._super();
    },
});

