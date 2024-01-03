#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class ResCityZip(models.Model):
    _inherit = "res.city.zip"

    display_name = fields.Char(
        compute="_compute_display_name", store=True, index="trigram"
    )

    @api.depends("name", "city_id", "state_id", "country_id")
    def _compute_display_name(self):
        names = dict(self.with_context({}).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if not (name == "" and operator == "ilike"):
            if name.split():
                args += [("display_name", operator, n) for n in name.split()]
                return self._search(args, limit=limit, access_rights_uid=name_get_uid)
            if name.starts_with("/"):
                # Start with '/' to search by code
                code = name[1:]
                if len(code) == 4 and code.isdigit():
                    args += [("district_code", operator, code)]
                if len(code) == 6 and code.isdigit():
                    args += [("sub_district_code", operator, code)]
                return self._search(args, limit=limit, access_rights_uid=name_get_uid)

        return super(ResCityZip, self)._name_search(
            name, args, operator, limit, name_get_uid
        )

    def name_get(self):
        """OVERRIDE Get the proper display name formatted as 'ZIP, name, state, country'.
        but for Thailand's zip we display as 'city, state, ZIP'"""
        res = []
        for rec in self:
            th = rec.city_id.country_id.code == "TH"
            name = [rec.name, rec.city_id.name] if not th else [rec.city_id.name]
            if rec.city_id.state_id:
                name.append(rec.city_id.state_id.name)
            if rec.city_id.country_id and not th:
                name.append(rec.city_id.country_id.name)
            if th:
                name.append(rec.name)
            res.append((rec.id, ", ".join(name)))
        return res
