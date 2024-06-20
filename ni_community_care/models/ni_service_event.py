#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ServiceLogging(models.Model):
    _inherit = "ni.service.event"

    outcome = fields.Html()
    outcome_id = fields.Many2one("ni.service.event.outcome")


class ServiceOutcome(models.Model):
    _name = "ni.service.event.outcome"

    _description = "Service Outcome"
