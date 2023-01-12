Advanced user access rights
---------------------------
This module allow the administrator to configure advanced access rights for users,the odoo default access rights are at 2 levels:<br/>
* __Model level__:At this level,the administrator can assign access rights to specific model (__CRUD__ operations) to users but through groups and not directly at user level.
* __Record level__:At this level,the administrator can assign the access of the user not to the model but to specific record that match the conditions specified in the rule.

The disadvantage of the first level (record level) is that we cannot assign specific access to a user without going through the group and in the some cases where we have users with access that may vary and customized comparing to their initial group, the management will be complex,<br/> although the second level can solve some inconvenience,it remains limited at the level of the objects.<br/><br/>
This module offers another layer of customization of access rights that can work with both levels, and which can give the administrator the possibility of assigning access rights directly to the user and at the levels of __Views__ and __Menus__, this will enrich the management of access rights and make it more flexible and adaptable to different uses cases (including complex ones).

