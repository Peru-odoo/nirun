#  Copyright (c) 2024 NSTDA
import ast

from odoo import _, fields, models


class EncounterBulk(models.TransientModel):
    _name = "ni.encounter.bulk"
    _description = "รับบริการ"

    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    class_id = fields.Many2one(
        "ni.encounter.class", default=lambda self: self.env.company.encounter_class_id
    )
    period_start = fields.Datetime(default=lambda _: fields.Datetime.now())
    patient_ids = fields.Many2many("ni.patient", required=True, check_company=True)
    calendar_id = fields.Many2one(
        "resource.calendar",
        check_company=True,
        required=True,
        default=lambda self: self.env.company.service_calendar_id,
    )

    def action_create(self):
        pat_ids = [
            {
                "class_id": self.class_id.id,
                "patient_id": p.id,
                "period_start": self.period_start,
                "resource_calendar_id": self.calendar_id.id,
            }
            for p in self.patient_ids
        ]
        pats = self.env["ni.encounter"].create(pat_ids)
        for p in pats:
            p.action_generate_service_resource()
        return self.action_view_encounter()

    def action_view_encounter(self):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_patient.ni_encounter_action")
        )
        action["display_name"] = _(
            "%(name)s's Encounter", name=self.period_start.date()
        )
        action["domain"] = [("period_start_date", "=", self.period_start)]
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        action["context"] = context
        return action
