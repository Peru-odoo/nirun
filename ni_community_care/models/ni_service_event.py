#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ServiceEvent(models.Model):
    _inherit = "ni.service.event"

    attendance_id = fields.Many2one(required=False)

    outcome = fields.Html("ผลการให้ความช่วยเหลือ")
    outcome_id = fields.Many2one("ni.service.event.outcome", "ผลการให้ความช่วยเหลือ")
    patient_id = fields.Many2one("ni.patient", store=False)
    service_category_id = fields.Many2one(store=True)

    prediction_id = fields.Many2one("ni.risk.assessment.prediction")
    plan_patient_ids = fields.Many2many(string="ผู้สูงอายุ")
