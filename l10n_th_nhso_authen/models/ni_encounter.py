#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    claim_code = fields.Char()
