from odoo import fields, models


class Goal(models.Model):
    _inherit = "ni.goal"

    careplan_id = fields.Many2one(
        "ni.careplan", index=True, help="What goal fulfills", ondelete="cascade"
    )
