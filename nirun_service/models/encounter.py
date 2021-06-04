#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    service_request_ids = fields.One2many(
        "ni.service.request", "encounter_id", "Service Requests",
    )
    service_request_count = fields.Integer(
        "Services", compute="_compute_service_request_count", sudo_compute=True
    )

    @api.depends("service_request_ids")
    def _compute_service_request_count(self):
        count = self._count_active_service_request()
        for rec in self:
            rec.service_request_count = count.get(rec.id)

    def _count_active_service_request(self):
        _domain = [("encounter_id", "in", self.ids), ("state", "=", "active")]
        req = self.env["ni.service.request"].read_group(
            _domain, ["encounter_id"], ["encounter_id"],
        )
        return {data["encounter_id"][0]: data["encounter_id_count"] for data in req}

    def open_service_request(self):
        self.ensure_one()
        enc = self
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": enc.patient_id.id,
                "search_default_active": True,
                "search_default_group_by_patient": True,
                "search_default_group_by_encounter": True,
                "default_patient_id": enc.patient_id.id,
                "default_encounter_id": enc.id,
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_service", "service_request_action"
        )
        return dict(action, context=ctx)