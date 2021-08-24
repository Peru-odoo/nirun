#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CarePlan(models.Model):
    _name = "ni.careplan"
    _description = "Care Plan"
    _inherit = ["period.mixin", "mail.thread", "ni.patient.res"]
    _check_company_auto = True
    _order = "sequence, id DESC"

    _rec_name = "id"

    patient_id = fields.Many2one(readonly=True, states={"draft": [("readonly", False)]})
    encounter_id = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    sequence = fields.Integer(
        "Sequence", help="Determine the display order", index=True, default=16
    )
    description = fields.Html(copy=True, help="Summary of nature of plan")

    patient_avatar = fields.Image(
        related="patient_id.image_512", attactment=False, store=False
    )
    category_ids = fields.Many2many(
        "ni.careplan.category",
        "ni_careplan_category_rel",
        "careplan_id",
        "category_id",
        store=True,
        readonly=False,
        compute="_compute_activity_category",
    )
    intent = fields.Selection(
        [
            ("order", "Order"),
            ("plan", "Plan"),
            ("proposal", "Proposal"),
            ("option", "Option"),
        ],
        default="plan",
        help="Indicating the degree of authority/intentionality of care plan.",
    )
    author_id = fields.Many2one(
        "res.users", string="Author", default=lambda self: self.env.user, tracking=True
    )
    manager_id = fields.Many2one("hr.employee", string="Care Manager", tracking=True)
    contributor_ids = fields.Many2many(
        "hr.employee", "ni_care_plan_contributor", "careplan_id", "contributor_id"
    )
    patient_contribution = fields.Boolean(
        default=False, help="Whether patient have contribution in this care plan"
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "In-Progress"),
            ("on-hold", "On-Hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
        ],
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(
        default=True,
        help="If the active field is set to False, it will allow you to"
        " hide the care plan without removing it.",
    )
    activity_ids = fields.One2many(
        "ni.careplan.activity",
        "careplan_id",
        string="Activities",
        readonly=True,
        check_company=True,
        states={"draft": [("readonly", False)], "active": [("readonly", False)]},
    )
    activity_count = fields.Integer(compute="_compute_activities_count", store=True)

    def name_get(self):
        res = []
        for plan in self:
            name = plan._get_name()
            res.append((plan.id, name))
        return res

    def _get_name(self):
        plan = self
        name = "#%d" % plan.id if plan.id else ""
        if self.env.context.get("show_patient"):
            name = "{} {}".format(plan.patient_id.name, name)
        return name

    @api.onchange("encounter_id")
    def _onchange_encounter_id(self):
        if self.encounter_id.period_start:
            self.period_start = self.encounter_id.period_start
        if self.encounter_id.period_end:
            self.period_end = self.encounter_id.period_end

    @api.depends("activity_ids")
    def _compute_activities_count(self):
        activities = self.env["ni.careplan.activity"].read_group(
            [("careplan_id", "in", self.ids)], ["careplan_id"], ["careplan_id"]
        )
        result = {
            data["careplan_id"][0]: data["careplan_id_count"] for data in activities
        }
        for plan in self:
            plan.activity_count = result.get(plan.id, 0)

    @api.depends("category_ids", "activity_ids.category_id")
    def _compute_activity_category(self):
        for plan in self:
            c1 = plan.mapped("activity_ids.category_id.id")
            c2 = plan.mapped("category_ids.id")
            plan.category_ids = list(set().union(c1, c2))

    def write(self, vals):
        if "active" in vals:
            self.with_context(active_test=False).mapped("activity_ids").write(
                {"active": vals["active"]}
            )
        return super().write(vals)

    # -------------
    # Actions
    # -------------
    def open_activity(self):
        self.ensure_one()
        ctx = dict(self._context)
        ctx.update(
            {"search_default_careplan_id": self.id, "default_careplan_id": self.id}
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action_from_careplan"
        )
        return dict(action, context=ctx)

    @api.model
    def open_sub_careplan(self):
        ctx = dict(self._context)
        ctx.update({"search_default_parent_id": self.id})
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_careplan", "careplan_activity_action_from_careplan"
        )
        return dict(action, context=ctx)

    def action_revoked(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
        self.write({"state": "revoked"})

    def action_hold_on(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
        self.write({"state": "on-hold"})

    def action_resume(self):
        for plan in self:
            if plan.state != "on-hold":
                raise UserError(_("Must be on-hold state"))
        self.write({"state": "active"})

    def action_confirm(self):
        self.write({"state": "active"})

    def action_close(self):
        for plan in self:
            if plan.state != "active":
                raise UserError(_("Must be active state"))
            else:
                plan.update({"state": "completed"})
                if not plan.period_end:
                    plan.period_end = fields.Date.today()
