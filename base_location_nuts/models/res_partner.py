# -*- coding: utf-8 -*-
# Python source code encoding : https://www.python.org/dev/peps/pep-0263/
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2015 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Antonio Espinosa <antonioea@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
import collections


def dict_recursive_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = dict_recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


class ResPartner(models.Model):
    _inherit = 'res.partner'

    region = fields.Many2one(comodel_name='res.partner.nuts',
                             string="Region", ondelete='set null')
    substate = fields.Many2one(comodel_name='res.partner.nuts',
                               string="Substate", ondelete='set null')

    @api.multi
    def onchange_state(self, state_id):
        result = super(ResPartner, self).onchange_state(state_id)
        if not state_id:
            changes = {
                'domain': {
                    'substate': [],
                    'region': [],
                },
                'value': {
                    'substate': False,
                    'region': False,
                }
            }
            dict_recursive_update(result, changes)
        return result

    @api.onchange('substate', 'region')
    def onchange_substate_or_region(self):
        result = {'domain': {}}
        if not self.substate:
            result['domain']['substate'] = []
        if not self.region:
            result['domain']['region'] = []
        return result
