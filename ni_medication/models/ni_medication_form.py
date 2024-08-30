#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class MedicationForm(models.Model):
    _name = "ni.medication.form"
    _description = "Medication Form"
    _inherit = ["ni.coding"]

    name_length = fields.Integer(compute="_compute_name_length")

    @api.depends("name")
    def _compute_name_length(self):
        for rec in self:
            rec.name_length = len(rec.name)

    medication_ids = fields.One2many("ni.medication", "form_id")

    def _extract_from_name(self):
        forms = self.search([], order="name_length desc")
        for form in forms:
            meds = self.env["ni.medication"].search(
                [("form_id", "=", False), ("name", "ilike", forms.name)]
            )
            if meds:
                meds.write({"form_id": form.id})
