#  Copyright (c) 2024 NSTDA
from odoo import models


class ServiceEventOutcome(models.Model):
    _name = "ni.service.event.outcome"
    _description = "Service Outcome"
    _inherit = ["ni.coding"]
