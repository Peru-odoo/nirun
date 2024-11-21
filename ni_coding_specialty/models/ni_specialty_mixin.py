#  Copyright (c) 2024 NSTDA
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SpecialtyMixin(models.AbstractModel):
    _name = "ni.specialty.mixin"
    _description = "Specialty mixin"

    specialty_ids = fields.Many2many("hr.job")

    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        user = self.env.user
        if (
            self._context.get("specialty_test", True)
            and user.employee_id.job_id
            and not user.has_group("base.group_no_one")
        ):
            _logger.debug(
                "Filter coding({}) for specialty={}".format(
                    self._name, user.employee_id.job_id
                )
            )
            domain += [
                "|",
                ("specialty_ids", "=", False),
                ("specialty_ids", "=", user.employee_id.job_id.id),
            ]
        return super()._search(domain, offset, limit, order, count, access_rights_uid)
