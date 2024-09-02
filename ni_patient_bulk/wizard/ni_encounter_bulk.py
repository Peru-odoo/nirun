#  Copyright (c) 2024 NSTDA
import ast
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


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
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
        ],
        string="Status",
        default="confirm",
    )

    def action_create(self):
        pat_ids = [
            {
                "class_id": self.class_id.id,
                "patient_id": p.id,
                "period_start": self.period_start,
                "period_start_date": self.period_start.date(),
                "resource_calendar_id": self.calendar_id.id,
            }
            for p in self.patient_ids
        ]
        pats = self.env["ni.encounter"].create(pat_ids)
        _logger.info("Created bulk encounters {}".format(pats.ids))
        for p in pats:
            p.action_generate_service_resource()
        _logger.debug("Generated service for Encounters {}".format(pats.ids))
        if self.state == "confirm":
            _logger.debug("Confirming encounter")
            pats.action_confirm()
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
        action["domain"] = [("period_start_date", "=", self.period_start.date())]
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update({"search_default_encounter": True})
        action["context"] = context
        return action
