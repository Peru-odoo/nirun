#  Copyright (c) 2024 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    coverage_type_id = fields.Many2one(
        "ni.coverage.type",
        "Use Coverage",
        readonly=False,
        store=True,
        domain="[('id', 'in', coverage_type_ids)]",
    )

    @api.onchange("patient_id", "coverage_type_ids")
    def _onchange_patient_coverage(self):
        for rec in self:
            if not rec.coverage_type_ids:
                rec.coverage_type_id = None
                continue
            if (
                not rec.coverage_type_id
                or rec.coverage_type_id.id not in rec.coverage_type_ids.ids
            ):
                rec.coverage_type_id = rec.coverage_type_ids[0]
