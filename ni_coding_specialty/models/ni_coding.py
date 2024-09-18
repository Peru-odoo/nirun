#  Copyright (c) 2024 NSTDA

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class Coding(models.AbstractModel):
    _name = "ni.coding"
    _inherit = ["ni.coding", "ni.specialty.mixin"]
