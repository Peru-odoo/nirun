#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class GoalCodeableConcept(models.Model):
    _name = "ni.goal.code"
    _description = "Goal Codeable Concept"
    _inherit = "ni.coding"

    category_id = fields.Many2one("ni.goal.category", index=True)
    specialty_ids = fields.Many2many(
        "hr.job",
        "ni_goal_code_specialty",
        "code_id",
        "job_id",
        help="Specialty who can assign this goal",
    )