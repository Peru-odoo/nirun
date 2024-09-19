#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class CareplanCategory(models.Model):
    _name = "ni.careplan.category"
    _description = "Careplan Category"
    _inherit = ["ni.coding"]

    _parent_store = True

    parent_id = fields.Many2one("ni.careplan.category", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    condition_code_ids = fields.Many2many(
        "ni.condition.code", "ni_careplan_category_condition_code"
    )
    goal_category_id = fields.Many2one("ni.goal.category", help="Default goal category")
    goal_code_ids = fields.Many2many("ni.goal.code", "ni_careplan_category_goal_code")
    service_category_id = fields.Many2one(
        "ni.service.category", help="Default service category"
    )

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
