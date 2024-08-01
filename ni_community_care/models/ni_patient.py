#  Copyright (c) 2024 NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    family_count = fields.Integer("จำนวนสมาชิกในครอบครัว")
    family_relation = fields.Many2one("ni.family.relation", "ความสัมพันธ์ในครับครัว")

    type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    type_decoration = fields.Selection(related="type_id.decoration")
    line = fields.Char("LINE ID")

    plan = fields.Text("แนวทางในการให้ความช่วยเหลือดูแล")

    plan_service_ids = fields.Many2many(
        "ni.service",
        "ni_patient_service_plan",
        "patient_id",
        "service_id",
        "แผนกิจกรรม",
    )
    risk_assessment_ids = fields.One2many("ni.risk.assessment", "patient_id")
    risk_assessment_id = fields.Many2one(
        "ni.risk.assessment", compute="_compute_risk_assessment", store=True
    )
    planned_all = fields.Boolean(related="risk_assessment_id.planned_all")
    actual_ratio = fields.Float(related="risk_assessment_id.actual_ratio")

    risk_assessment_count = fields.Integer(compute="_compute_risk_assessment")
    attend_event_id = fields.Many2many("ni.service.event", "ni_patient_service_attend")

    condition_other = fields.Char()
    allergy_other = fields.Char()

    @api.depends("risk_assessment_ids")
    def _compute_risk_assessment(self):
        for rec in self:
            rec.risk_assessment_count = len(rec.risk_assessment_ids)
            rec.risk_assessment_id = (
                rec.risk_assessment_ids[0] if rec.risk_assessment_ids else None
            )

    def action_risk(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self.id,
            }
        )
        view = {
            "name": "Risk Assessment",
            "res_model": "ni.risk.assessment",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_type": "form",
            "views": [[False, "form"]],
            "context": ctx,
        }
        return view


class PatientType(models.Model):
    _name = "ni.patient.type"
    _inherit = "ni.coding"

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


class FamilyRelation(models.Model):
    _name = "ni.family.relation"
    _inherit = "ni.coding"
