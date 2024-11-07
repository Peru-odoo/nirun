#  Copyright (c) 2024 NSTDA
import ast
from pprint import pprint

from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    family_count = fields.Integer("จำนวนสมาชิกในครอบครัว")
    family_relation = fields.Many2one("ni.family.relation", "ความสัมพันธ์ในครับครัว")

    type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    type_decoration = fields.Selection(related="type_id.decoration")
    line = fields.Char("LINE ID")

    service_event_ids = fields.One2many(
        "ni.service.event", compute="_compute_service_event"
    )
    service_event_count = fields.Integer(compute="_compute_service_event")

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

    heal_progress = fields.Boolean(default=False, compute="_compute_category_progress")
    soci_progress = fields.Boolean(default=True, compute="_compute_category_progress")
    econ_progress = fields.Boolean(default=True, compute="_compute_category_progress")
    envi_progress = fields.Boolean(default=False, compute="_compute_category_progress")
    tech_progress = fields.Boolean(default=True, compute="_compute_category_progress")

    @api.depends("service_event_ids")
    def _compute_category_progress(self):
        for rec in self:
            grp = self.env["ni.service.event"].read_group(
                [("plan_patient_ids", "=", rec.id)], ["count"], "service_category_id"
            )
            rec.heal_progress = True
            for g in grp:
                cat_id = self.env["ni.service.category"].browse(
                    g.get("service_category_id")[0]
                )
                f = "{}_progress".format(cat_id["code"])
                if f in self._fields:
                    rec[f] = bool(g.get("service_category_id_count"))

    def action_view_service_event(self):
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            ._for_xml_id("ni_community_care.ni_service_event_action_from_patient")
        )
        action["display_name"] = _("%(name)s's Service", name=self.name)
        context = action["context"].replace("active_id", str(self.id))
        context = ast.literal_eval(context)
        context.update(
            {
                "create": self.active,
                "active_test": self.active,
                "default_plan_patient_ids": [fields.Command.set(self.ids)],
            }
        )
        action["view_mode"] = "kanban,calendar,tree,pivot,form"
        action["context"] = context
        pprint(action)
        return action

    def _compute_service_event(self):
        for rec in self:
            event = self.env["ni.service.event"].search(
                [("plan_patient_ids", "=", rec.id)], order="start desc"
            )
            rec.service_event_ids = event
            rec.service_event_count = len(event)

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

    def action_survey_subject(self):
        action_rec = self.env.ref("survey_subject.survey_subject_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_subject_ni_patient": self.id,
            }
        )
        action["context"] = ctx
        return action


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
