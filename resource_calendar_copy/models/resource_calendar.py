#  Copyright (c) 2024 NSTDA
from odoo import models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def action_copy_wizard(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_calendar_id": self.id,
            }
        )
        view = {
            "name": "Copy Attendance Wizard",
            "res_model": "resource.calendar.attendance.copy.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "view_mode": "form",
            "context": ctx,
        }
        return view
