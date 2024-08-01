#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ServiceEvent(models.Model):
    _inherit = "ni.service.event"

    attendance_id = fields.Many2one(required=False)

    outcome = fields.Html()
    outcome_id = fields.Many2one("ni.service.event.outcome", "ผลการให้ความช่วยเหลือ")
    patient_id = fields.Many2one("ni.patient", store=False)

    prediction_id = fields.Many2one("ni.risk.assessment.prediction")
