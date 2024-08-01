#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    careplan_ids = fields.One2many("ni.careplan", "patient_id")
    careplan_count = fields.Integer(compute="_compute_careplan_count")

    goal_ids = fields.One2many("ni.goal", "patient_id")

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for rec in self:
            rec.careplan_count = len(rec.careplan_ids)
