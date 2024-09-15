#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class CareplanCategory(models.Model):
    _name = "ni.careplan.category"
    _description = "Careplan Category"
    _inherit = ["ni.coding"]

    condition_code_ids = fields.Many2many("ni.condition.code")
    goal_category_id = fields.Many2one("ni.goal.category")
    service_category_id = fields.Many2one("ni.service.category")
