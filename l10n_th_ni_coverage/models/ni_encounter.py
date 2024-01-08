#  Copyright (c) 2024 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    coverage_type_id = fields.Many2one(
        "ni.coverage.type",
        "Coverage",
        domain="[('parent_id', '!=', False)]",
        compute="_compute_coverage_type_ids",
        readonly=False,
        store=True,
    )
    coverage_type_parent_id = fields.Many2one(
        related="coverage_type_id.parent_id", string="Coverage Group"
    )

    @api.depends("coverage_type_ids")
    def _compute_coverage_type_ids(self):
        for rec in self:
            if rec.coverage_type_ids:
                rec.coverage_type_id = rec.coverage_type_ids[0]
            else:
                rec.coverage_type_ids = False
