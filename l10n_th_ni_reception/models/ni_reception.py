#  Copyright (c) 2021-2023. NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Reception(models.Model):
    _inherit = ["ni.reception"]

    zip_id = fields.Many2one(
        comodel_name="res.city.zip",
        string="ZIP Location",
        index=True,
        compute="_compute_zip_id",
        readonly=False,
        store=True,
    )
    city_id = fields.Many2one(
        "res.city",
        index=True,  # add index for performance
        compute="_compute_city_id",
        readonly=False,
        store=True,
    )
    city = fields.Char(compute="_compute_city", readonly=False, store=True)
    zip = fields.Char(compute="_compute_zip", readonly=False, store=True)
    country_id = fields.Many2one(
        "res.country", compute="_compute_country_id", readonly=False, store=True
    )
    country_enforce_cities = fields.Boolean()
    state_id = fields.Many2one(compute="_compute_state_id", readonly=False, store=True)

    coverage_type_id = fields.Many2one(
        "ni.coverage.type",
        "Coverage",
        domain="['|', ('child_count', '=', 0), ('parent_id', '!=', False)]",
        compute="_compute_coverage_type_ids",
        readonly=False,
        store=True,
    )
    coverage_type_parent_id = fields.Many2one(
        related="coverage_type_id.parent_id", string="Coverage Group"
    )

    @api.depends("coverage_type_ids")
    def _compute_coverage_type_ids(self):
        for rec in self:
            if rec.coverage_type_ids:
                rec.coverage_type_id = rec.coverage_type_ids[0]
            else:
                rec.coverage_type_ids = False

    @api.depends("state_id", "country_id", "city_id", "zip")
    def _compute_zip_id(self):
        """Empty the zip auto-completion field if data mismatch when on UI."""
        for record in self.filtered("zip_id"):
            fields_map = {
                "zip": "name",
                "city_id": "city_id",
                "state_id": "state_id",
                "country_id": "country_id",
            }
            for rec_field, zip_field in fields_map.items():
                if (
                    record[rec_field]
                    and record[rec_field] != record._origin[rec_field]
                    and record[rec_field] != record.zip_id[zip_field]
                ):
                    record.zip_id = False
                    break

    @api.depends("zip_id")
    def _compute_city_id(self):
        if hasattr(super(), "_compute_city_id"):
            return super()._compute_city_id()  # pragma: no cover
        for record in self:
            if record.zip_id:
                record.city_id = record.zip_id.city_id
            elif not record.country_enforce_cities:
                record.city_id = False

    @api.depends("zip_id")
    def _compute_city(self):
        for record in self:
            if record.zip_id:
                record.city = record.zip_id.city_id.name
        for record in self:
            if record.zip_id and record.country_id.code == "TH":
                address = record.zip_id.city_id.name.split(", ")
                record.update({"street2": address[0], "city": address[1]})

    @api.depends("zip_id")
    def _compute_zip(self):
        if hasattr(super(), "_compute_zip"):
            return super()._compute_zip()  # pragma: no cover
        for record in self:
            if record.zip_id:
                record.zip = record.zip_id.name

    @api.depends("zip_id", "state_id")
    def _compute_country_id(self):
        if hasattr(super(), "_compute_country_id"):
            return super()._compute_country_id()  # pragma: no cover
        for record in self:
            if record.zip_id.city_id.country_id:
                record.country_id = record.zip_id.city_id.country_id
            elif record.state_id:
                record.country_id = record.state_id.country_id

    @api.depends("zip_id")
    def _compute_state_id(self):
        if hasattr(super(), "_compute_state_id"):
            return super()._compute_state_id()  # pragma: no cover
        for record in self:
            state = record.zip_id.city_id.state_id
            if state and record.state_id != state:
                record.state_id = record.zip_id.city_id.state_id

    @api.constrains("zip_id", "country_id", "city_id", "state_id", "zip")
    def _check_zip(self):
        if self.env.context.get("skip_check_zip"):
            return
        for rec in self:
            if not rec.zip_id:
                continue
            error_dict = {"partner": rec.name, "location": rec.zip_id.name}
            if rec.zip_id.city_id.country_id != rec.country_id:
                raise ValidationError(
                    _(
                        "The country of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.zip_id.city_id.state_id != rec.state_id:
                raise ValidationError(
                    _(
                        "The state of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.zip_id.city_id != rec.city_id:
                raise ValidationError(
                    _(
                        "The city of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )
            if rec.zip_id.name != rec.zip:
                raise ValidationError(
                    _(
                        "The zip of the partner %(partner)s differs from that in "
                        "location %(location)s"
                    )
                    % error_dict
                )

    def _get_patient_field(self):
        return super(Reception, self)._get_patient_field() + ["zip_id", "city_id"]

    def _get_encounter_field(self):
        return super(Reception, self)._get_encounter_field() + ["coverage_type_id"]
