#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class Service(models.Model):
    _inherit = "ni.service"

    objective = fields.Html("วัตถุประสงค์")
    procedure = fields.Html("ขั้นตอนการดำเนินงาน")
    benefit = fields.Html("ประโยชน์ที่ได้รับ")
    target = fields.Integer("จำนวนเป้าหมาย")
    target_type_ids = fields.Many2many(
        "ni.patient.type",
        "ni_service_target_type",
        "service_id",
        "type_id",
        "กลุ่มเป้าหมาย",
    )
    description = fields.Html("หมายเหตุ")

    category_color = fields.Integer(related="category_id.color")


class ServiceCalendar(models.Model):
    _inherit = "ni.service.event"

    attend_patient_ids = fields.Many2many(
        "ni.patient", "ni_patient_service_attend", check_company=True
    )
