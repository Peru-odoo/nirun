#  Copyright (c) 2024 NSTDA

from odoo import api, models


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    @api.model
    def get_all_dayofweek_label(self):
        dow = dict(self._fields["dayofweek"].selection)
        return [v for k, v in dow.items()]

    def action_copy_other_day(self, dayofweek=None):
        dayofweek = [] if not dayofweek else list(dayofweek)
        res = []
        for rec in self:
            name = rec._get_name_pattern()
            for day in dayofweek:
                copy_rec = rec.copy(
                    {
                        "name": name.format(
                            dow=dict(self._fields["dayofweek"].selection).get(day)
                        ),
                        "dayofweek": day,
                        "sequence": rec.sequence + len(self),
                    }
                )
                res.append(copy_rec)
        return res

    def _get_name_pattern(self):
        self.ensure_one()

        name = self.name
        for day in self.get_all_dayofweek_label():
            if day in name:
                return name.replace(day, "{dow}")
        return name + " ({dow})"
