#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class Benefit(models.Model):
    _name = "ni.benefit"
    _description = "Person Benefit"
    _inherit = "ni.coding"

    _parent_store = True

    parent_id = fields.Many2one("ni.benefit", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
