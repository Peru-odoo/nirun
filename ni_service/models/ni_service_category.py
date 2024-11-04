#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class ServiceCategory(models.Model):
    _name = "ni.service.category"
    _description = "Service Category"
    _inherit = "ni.coding"

    _parent_store = True

    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )

    parent_id = fields.Many2one("ni.service.category", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)
    service_ids = fields.One2many("ni.service", "category_id")
    specialty_ids = fields.Many2many(
        "hr.job", "ni_service_category_specialty", "category_id", "job_id"
    )
    fold = fields.Boolean(default=False)

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
