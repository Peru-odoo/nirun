#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models
from odoo.fields import Command
from odoo.tools.date_utils import relativedelta

LOCK_STATE_DICT = {
    "revoked": [("readonly", True)],
    "completed": [("readonly", True)],
}


class Careplan(models.Model):
    _name = "ni.careplan"
    _description = "Care Plan"
    _inherit = ["ni.workflow.request.mixin", "ni.period.mixin", "ni.identifier.mixin"]
    _check_period_start = False

    @api.model
    def default_get(self, fields):
        res = super(Careplan, self).default_get(fields)
        res["intent"] = "plan"
        return res

    period_start = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda _: fields.Datetime.now().replace(day=1),
    )
    period_end = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda _: fields.Datetime.now()
        + relativedelta(day=1, months=3, days=-1),
    )
    category_id = fields.Many2one(
        "ni.careplan.category",
        required=True,
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    condition_ids = fields.Many2many(
        "ni.condition",
        "ni_careplan_condition",
        "plan_id",
        "condition_id",
        domain="[('patient_id', '=', patient_id), ('clinical_state', '=', 'active')]",
        context={"default_patient_id": "patient_id"},
        states=LOCK_STATE_DICT,
    )
    condition_count = fields.Integer(compute="_compute_condition_count")
    goal_mode = fields.Selection(
        [("simple", "Simple"), ("advance", "Advance")], default="advance", required=True
    )
    goal_code_ids = fields.Many2many(
        "ni.goal.code",
        domain="['|', ('specialty_ids', '=', False), ('specialty_ids', '=', user_specialty)]",
    )
    goal_text = fields.Html()
    goal_category_id = fields.Many2one(related="category_id.goal_category_id")
    goal_ids = fields.One2many(
        "ni.goal",
        "careplan_id",
        context={"default_patient_id": "patient_id"},
        states=LOCK_STATE_DICT,
    )
    goal_review_ids = fields.One2many(related="goal_ids", string="Goal Review")
    goal_count = fields.Integer(compute="_compute_goal_ratio")
    goal_achieved_count = fields.Integer(compute="_compute_goal_ratio")
    goal_ratio = fields.Float(compute="_compute_goal_ratio")

    action_count = fields.Integer(compute="_compute_action_count")
    action_display = fields.Selection(
        [
            ("service", "Service"),
            ("medication", "Medication"),
        ],
        default="service",
    )
    service_category_id = fields.Many2one(related="category_id.service_category_id")
    service_request_ids = fields.One2many(
        "ni.service.request",
        "careplan_id",
        domain="[('category_id', '=?', service_category_id), ('intent', '=', 'plan')]",
        options="{'create': true}",
        states=LOCK_STATE_DICT,
    )
    service_request_count = fields.Integer(compute="_compute_action_count")
    medication_request_ids = fields.One2many(
        "ni.medication.request", "careplan_id", states=LOCK_STATE_DICT
    )
    medication_request_count = fields.Integer(compute="_compute_action_count")
    document_ids = fields.One2many(
        "ni.document.ref", "careplan_id", states=LOCK_STATE_DICT
    )
    document_count = fields.Integer(compute="_compute_document_count")
    achievement_id = fields.Many2one(
        "ni.goal.achievement", domain=[("careplan", "=", True)], states=LOCK_STATE_DICT
    )
    achievement_reason = fields.Html(help="Reason for current achievement")
    achievement_date = fields.Datetime(
        help="When achievement status took effect", readonly=1
    )
    achievement_uid = fields.Many2one("res.users", readonly=1)

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.category_id and rec.category_id.condition_code_ids:
                condition = self.env["ni.condition"].search(
                    [
                        ("partner_id", "=", self.partner_id.ids[0]),
                        ("code_id", "in", rec.category_id.condition_code_ids.ids),
                        ("clinical_state", "=", "active"),
                    ]
                )
                rec.condition_ids = condition
            else:
                rec.condition_ids = None

    @api.depends("condition_ids")
    def _compute_condition_count(self):
        for rec in self:
            rec.condition_count = len(rec.condition_ids)

    @api.depends("service_request_ids", "medication_request_ids")
    def _compute_action_count(self):
        for rec in self:
            rec.service_request_count = len(rec.service_request_ids)
            rec.medication_request_count = len(rec.medication_request_ids)
            rec.action_count = sum(
                [rec.service_request_count, rec.medication_request_count]
            )

    @api.depends("goal_ids")
    def _compute_goal_ratio(self):
        for rec in self:
            rec.goal_count = len(rec.goal_ids)
            rec.goal_achieved_count = len(
                rec.goal_ids.filtered_domain(
                    [
                        (
                            "achievement_id",
                            "child_of",
                            self.env.ref("ni_goal.goal_achieved").id,
                        )
                    ]
                )
            )
            rec.goal_ratio = (
                rec.goal_achieved_count / rec.goal_count * 100
                if rec.goal_count
                else 0.0
            )

    def write(self, vals):
        if "achievement_id" in vals:
            vals["achievement_date"] = fields.Datetime.now()
            vals["achievement_uid"] = self.env.user.id
            vals["state"] = "completed"
        return super(Careplan, self).write(vals)

    @api.depends("document_ids")
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    @api.constrains("service_request_ids")
    def _check_service_request(self):
        for rec in self:
            sr = rec.service_request_ids.filtered(
                lambda r: r.intent == "plan" and not r.careplan_id
            )
            if sr:
                sr.write({"careplan_id": rec.id})

    @api.constrains("goal_mode", "goal_code_ids")
    def _check_goal_text(self):
        default_state = self.env["ni.goal.state"].search([], limit=1)
        for rec in self:
            if rec.goal_mode == "simple":
                org_goal = rec.goal_ids.mapped("code_id")
                cmd = []
                for g in rec.goal_code_ids.filtered(lambda g: g not in org_goal):
                    cmd.append(
                        Command.create(
                            {
                                "patient_id": rec.patient_id.id,
                                "encounter_id": rec.encounter_id.id,
                                "name": g.name,
                                "code_id": g.id,
                                "category_id": g.category_id.id
                                if g.category_id
                                else None,
                                "state_id": default_state.id,
                            }
                        )
                    )
                for g in rec.goal_ids.filtered(
                    lambda g: g.code_id not in rec.goal_code_ids
                ):
                    cmd.append(Command.unlink(g.id))
                rec.goal_ids = cmd
