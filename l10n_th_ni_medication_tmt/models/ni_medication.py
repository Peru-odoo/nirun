#  Copyright (c) 2024 NSTDA

import pprint

from odoo import _, api, fields, models

class Medication(models.Model):
    _inherit = 'ni.medication'

    code = fields.Char()
    system_id = fields.Many2one('ni.coding.system')

    def _process_name(self):
        gpu_system = self.env.ref('l10n_th_ni_medication_tmt.system_tmt_gpu')
        for rec in self.filtered_domain([('system_id', '=', gpu_system.id)]):
            rec._process_gpu_name()

    def _process_gpu_name(self):
        pprint.pprint(self.name)
        if self.name.endswith("(GPU)"):
            names = self.name.replace('(GPU)', '').strip().split(',')
            amount = names[-1].strip()
            amounts = amount.split(' ')

            if len(amounts) == 3:
                de_unit = self._search_unit(amounts[2])
                num_unit = self._search_unit(amounts[1])

                st = float(amounts[0])
                if all([de_unit, num_unit, st]):
                    self.write({
                        'amount_numerator': st,
                        'amount_numerator_unit': num_unit[0].id,
                        'amount_denominator': 1,
                        'amount_denominator_unit': de_unit[0].id
                    })
            if len(amounts) == 2:
                de_unit = self._search_unit(amounts[1])
                de = float(amounts[0])
                self.write({
                    'amount_numerator': 1,
                    'amount_numerator_unit': None,
                    'amount_denominator': de,
                    'amount_denominator_unit': de_unit[0].id
                })

    def _search_unit(self, name):
        if not name:
            return None

        uom = self.env['uom.uom'].search(['|', ('name', 'ilike', name), ('alias', 'ilike', name)])
        if not uom:
            uom = self.env['uom.uom'].create({
                'name': name,
                'category_id': self.env.ref('uom.product_uom_categ_unit').id,
                'uom_type': 'smaller',
                'factor': 1
            })
        return uom


    @api.constrains('name', 'system_id')
    def _check_system(self):
        gpu_system = self.env.ref('l10n_th_ni_medication_tmt.system_tmt_gpu')
        gpu = self.filtered_domain([
            ('name', 'like', '%(GPU)'),
            ('system_id', '!=', gpu_system.id)
        ])
        gpu.write({'system_id': gpu_system.id})


