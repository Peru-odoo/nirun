#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class CommunityCareMontlyReport(models.Model):
    _name = "ni.cc.report.monthly"
    _inherit = "ni.identifier.mixin"
    _identifier_ts_field = "period_start"

    company_id = fields.Many2one(
        "res.company", "หน่วยงาน", default=lambda self: self.env.company, required=True
    )
    period_start = fields.Date(compute="_compute_year", store=True)
    period_end = fields.Date(compute="_compute_year", store=True)
    year = fields.Integer(
        "ประจำปี", compute="_compute_year", inverse="_inverse_year", store=True
    )
    year_th = fields.Char(
        "ประจำปี",
        required=True,
        default=lambda self: str(fields.Date.today().year + 543),
    )
    month = fields.Selection(
        [
            ("1", "มกราคม"),
            ("2", "กุมภาพันธ์"),
            ("3", "มีนาคม"),
            ("4", "เมษายน"),
            ("5", "พฤษภาคม"),
            ("6", "มิถุนายน"),
            ("7", "กรกฎาคม"),
            ("8", "สิงหาคม"),
            ("9", "กันยายน"),
            ("10", "ตุลาคม"),
            ("11", "พฤศจิกายน"),
            ("12", "ธันวาคม"),
        ],
        "ประจำเดือน",
        default=lambda self: str(fields.Date.today().month),
        required=True,
    )

    reporter_uid = fields.Many2one(
        "res.users", "ผู้ออกรายงาน", required=True, check_company=True
    )
    approver_uid = fields.Many2one(
        "res.users",
        "ผู้ตรวจสอบรายงาน",
        domain="[('id', '!=', reporter_uid)]",
        check_company=True,
    )
    approver_title = fields.Char(string="ตำแหน่ง", related="approver_uid.job_title")

    line_ids = fields.One2many("ni.cc.report.monthly.line", "report_id")

    _sql_constraints = [
        (
            "reporter_period_uniq",
            "unique (company_id,period_start)",
            "Report must be unique for each month!",
        ),
    ]

    @api.depends("year_th", "month")
    def _compute_year(self):
        for rec in self:
            rec.year = int(rec.year_th) - 543
            rec.period_start = fields.Date.today().replace(rec.year, int(rec.month), 1)
            rec.period_end = fields.Date.end_of(rec.period_start, "month")

    def _inverse_year(self):
        for rec in self:
            rec.year_th = str(rec.year + 543)

    def action_approve(self):
        self.write({"approver_uid": self.env.user.id})

    def action_generate(self):
        self.ensure_one()
        events = self.env["ni.service.event"].search(
            [("start", ">=", self.period_start), ("start", "<=", self.period_end)]
        )
        pid = events.mapped("attend_patient_ids")
        if pid:
            self.line_ids = [fields.Command.create({"patient_id": p.id}) for p in pid]
            self.line_ids._onchange_patient_id()


class CommunityCareReportLine(models.Model):
    _name = "ni.cc.report.monthly.line"
    _description = "Monthly Report Line"

    report_id = fields.Many2one(
        "ni.cc.report.monthly", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="report_id.company_id")
    patient_id = fields.Many2one(
        "ni.patient", string="ผู้รับบริการ", required=True, check_company=True
    )
    patient_type_id = fields.Many2one(related="patient_id.type_id")
    service_ids = fields.Many2many(
        "ni.service",
        string="การดูแล",
        check_company=True,
        domain="[('target_type_ids', '=', patient_type_id)]",
    )
    duration = fields.Float("ระยะเวลา", compute="_compute_duration")

    feedback = fields.Selection(
        [
            ("0", "ไม่มีผล"),
            ("1", "น้อยที่สุด"),
            ("2", "น้อย"),
            ("3", "ปานกลาง"),
            ("4", "มาก"),
            ("5", "มากที่สุด"),
        ],
        "รอยยิ้ม",
        default="0",
    )
    outcome = fields.Html("ผลการดูแล")

    _sql_constraints = [
        (
            "report_id_patient_id_uniq",
            "unique (report_id, patient_id)",
            "This patient in report must be unique",
        ),
    ]

    @api.onchange("patient_id")
    def _onchange_patient_id(self):
        for rec in self:
            if rec.patient_id:
                serv = self.env["ni.service.event"].search(
                    [
                        ("start", ">=", rec.report_id.period_start),
                        ("start", "<=", rec.report_id.period_end),
                        ("attend_patient_ids", "=", rec.patient_id.id),
                    ]
                )
                rec.service_ids = serv.mapped("service_id")

    @api.depends("service_ids")
    def _compute_duration(self):
        for rec in self:
            rec.duration = sum(rec.service_ids.mapped("duration"))
