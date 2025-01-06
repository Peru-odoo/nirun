#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    font = fields.Selection(
        selection_add=[("NotoSans", "NotoSans"), ("NotoSerif", "NotoSerif")]
    )
