#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    family_count = fields.Integer("จำนวนสมาชิกในครอบครัว")
    family_relation = fields.Many2one("ni.family.relation", "ความสัมพันธ์ในครับครัว")

    type_id = fields.Many2one("ni.patient.type", "ประเภทผู้สูงอายุ")
    problem_ids = fields.Many2one("ni.condition.code")
    problem = fields.Text()
    line = fields.Char("LINE ID")

    plan = fields.Text("แนวทางในการให้ความช่วยเหลือดูแล")

    plan_service_ids = fields.Many2many(
        "ni.service",
        "ni_patient_service_plan",
        "patient_id",
        "service_id",
        "แผนกิจกรรม",
    )

    attend_event_id = fields.Many2many("ni.service.event", "ni_patient_service_attend")


class PatientType(models.Model):
    _name = "ni.patient.type"
    _inherit = "ni.coding"


class FamilyRelation(models.Model):
    _name = "ni.family.relation"
    _inherit = "ni.coding"
