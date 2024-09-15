#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class CareplanCategory(models.Model):
    _inherit = "ni.careplan.category"

    observation_category_ids = fields.Many2many(
        "ni.observation.category",
        help="If this empty it mean careplan not address observation",
    )
    observation_category_count = fields.Integer(
        compute="_compute_observation_category_count"
    )
    observation_code_ids = fields.Many2many(
        "ni.observation.type",
        domain="[('category_id', 'in', observation_category_ids)]",
        help="Leave this empty if apply to all type of selected categories",
    )

    @api.depends("observation_category_ids")
    def _compute_observation_category_count(self):
        for rec in self:
            rec.observation_category_count = len(rec.observation_category_ids)
