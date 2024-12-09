#  Copyright (c) 2024 NSTDA
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SpecialtyMixin(models.AbstractModel):
    _name = "ni.specialty.mixin"
    _description = "Specialty mixin"

    specialty_ids = fields.Many2many("hr.job")
    _specialty_groups = "base.group_system"

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
            and not user.user_has_groups(self._specialty_groups)
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
        else:
            logging.debug(
                "Not filter coding({}) [specialty_test={}, job_id={}, not group({})={}]".format(
                    self._name,
                    self._context.get("specialty_test", True),
                    user.employee_id.job_id if user.employee_id else None,
                    self._specialty_groups,
                    not user.user_has_groups(self._specialty_groups),
                )
            )
        return super()._search(domain, offset, limit, order, count, access_rights_uid)
