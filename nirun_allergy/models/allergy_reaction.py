#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class AllergyReaction(models.Model):
    _name = "ni.allergy.reaction"
    _description = "Allergy Reaction Event"
    _order = "onset DESC"

    allergy_id = fields.Many2one(
        "ni.allergy",
        "Allergy / Intolerance",
        ondelete="cascade",
        index=True,
        required=True,
    )
    onset = fields.Datetime(
        help="Date(/time) when manifestations showed",
        required=True,
        default=lambda self: fields.Datetime.now(),
    )
    description = fields.Text(help="Description of the event as a whole")
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        default="mild",
        tracking=1,
        required=False,
    )
    note = fields.Text()