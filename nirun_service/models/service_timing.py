#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class HealthcareServiceTiming(models.Model):
    _name = "ni.service.timing"
    _description = "Healthcare Service Event Timing"
    _inherits = {"ni.timing": "timing_id"}
    _inherit = "ni.timing.mixin"

    service_id = fields.Many2one("ni.service", ondelete="cascade")
