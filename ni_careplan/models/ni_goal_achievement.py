#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class GoalAchievement(models.Model):
    _inherit = "ni.goal.achievement"

    careplan = fields.Boolean(
        help="Weather this state will appear on careplan achievement"
    )
