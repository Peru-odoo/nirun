#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Careplan(models.Model):
    _inherit = "ni.careplan"

    patient_observation_ids = fields.Many2many(
        "ni.patient.observation",
        compute="_compute_patient_observation",
        help="Selectable latest patient's observations filtered by category",
    )
    observation_category_ids = fields.Many2many(
        related="category_id.observation_category_ids"
    )
    observation_category_count = fields.Integer(
        related="category_id.observation_category_count"
    )
    observation_ids = fields.Many2many(
        "ni.observation",
        string="Reason",
        domain="[('id', 'in', patient_observation_ids)]",
        help="Use as reason of this careplan",
    )

    @api.depends("patient_id", "category_id")
    def _compute_patient_observation(self):
        for rec in self:
            if (
                rec.patient_id
                and rec.category_id
                and rec.category_id.observation_category_ids
            ):
                domain = [
                    ("patient_id", "=", rec.patient_id.ids[0]),
                ]
                domain += (
                    [("category_id", "in", rec.category_id.observation_category_ids)]
                    if not rec.category_id.observation_code_ids
                    else [("type_id", "in", rec.category_id.observation_code_ids.ids)]
                )
                observation = self.env["ni.patient.observation"].search(domain)
                rec.patient_observation_ids = observation
                rec.observation_ids = [
                    fields.Command.set(
                        observation.filtered_domain([("is_problem", "=", True)]).ids
                    )
                ]
            else:
                rec.patient_observation_ids = None
                rec.observation_ids = [fields.Command.clear()]
