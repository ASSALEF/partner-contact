# -*- coding: utf-8 -*-

#    Author: Nicolas Bessi. Copyright Camptocamp SA
#    Copyright (C)
#       2014:       Agile Business Group (<http://www.agilebg.com>)
#       2015:       Grupo ESOC <www.grupoesoc.es>
#       2015:       Antonio Espinosa <antonioea@antiun.com>
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

import logging
from openerp import api, fields, models, _
from . import exceptions


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Adds last name and first name; name becomes a stored function field."""
    _inherit = 'res.partner'

    firstname = fields.Char("First name")
    lastname = fields.Char("Last name")
    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True)

    @api.model
    def _get_computed_name(self, lastname, firstname):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        return u" ".join((p for p in (lastname, firstname) if p))

    @api.one
    @api.depends("firstname", "lastname", "company_id")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        names = (self.lastname, self.firstname)
        if self.company_id.names_order == 'first_last':
            names = reversed(names)
        self.name = u" ".join(filter(None, names))

    def _clean_field(self, field, default):
        value = getattr(self, field)
        clean = default
        if value and type(value) in (str, unicode):
            clean = u" ".join(value.split(None))
            if not clean:
                clean = default
        if value != clean:
            setattr(self, field, clean)

    @api.one
    def _inverse_name_after_cleaning_whitespace(self):
        """Clean whitespace in :attr:`~.name` and split it.

        Removes leading, trailing and duplicated whitespace.

        The splitting logic is stored separately in :meth:`~._inverse_name`, so
        submodules can extend that method and get whitespace cleaning for free.
        """
        # Remove unneeded whitespace
        self._clean_field('name', '')

        # Save name in the real fields
        if self.env.context.get("skip_onchange"):
            # Do not skip next onchange
            self.env.context = (
                self.with_context(skip_onchange=False).env.context)
        else:
            self._inverse_name()

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        """Try to revert the effect of :meth:`._compute_name`.

        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Company name goes to the lastname
        if is_company or not name:
            parts = [name or False, False]
        # Guess name splitting
        else:
            parts = self.name.split(" ")
            if len(parts) > 1:
                if self.company_id.names_order == 'first_last':
                    first = parts[0]
                    last = u" ".join(parts[1:])
                else:
                    last = parts[0]
                    first = u" ".join(parts[1:])
                parts = [last, first]
            else:
                while len(parts) < 2:
                    parts.append(False)

    @api.one
    def _inverse_name(self):
        parts = self._get_inverse_name(self.name, self.is_company)
        self.lastname, self.firstname = parts

    @api.one
    @api.constrains("firstname", "lastname")
    def _check_name(self):
        """Ensure at least one name is set."""
        if not (self.firstname or self.lastname):
            raise exceptions.EmptyNamesError(self)

    @api.one
    @api.onchange("firstname", "lastname")
    def _onchange_subnames(self):
        """Avoid recursion when the user changes one of these fields.

        This forces to skip the :attr:`~.name` inversion when the user is
        setting it in a not-inverted way.
        """
        self._clean_field('firstname', False)
        self._clean_field('lastname', False)

        # Modify self's context without creating a new Environment.
        # See https://github.com/odoo/odoo/issues/7472#issuecomment-119503916.
        self.env.context = self.with_context(skip_onchange=True).env.context

    @api.one
    @api.onchange("name")
    def _onchange_name(self):
        """Ensure :attr:`~.name` is inverted in the UI."""
        self._inverse_name_after_cleaning_whitespace()

    @api.multi
    def _clean_names(self, vals):
        fields = {
            'name': '',
            'firstname': False,
            'lastname': False,
        }
        for field, default in fields.iteritems():
            if vals.get(field, None) is not None:
                value = vals.get(field) if vals.get(field) else default
                if value and type(value) in (str, unicode):
                    value = u" ".join(value.split(None))
                    if not value:
                        value = default
                vals[field] = value
        return vals

    @api.multi
    def _precedence_check(self, vals):
        name = vals.get('name', False)
        firstname = vals.get('firstname', False)
        lastname = vals.get('lastname', False)
        if name and (firstname or lastname):
            # firstname or lastname have precedence
            vals.pop('name', None)
        return vals

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        if self.lastname:
            default['lastname'] = _('%s (copy)') % self.lastname
        elif self.firstname:
            default['firstname'] = _('%s (copy)') % self.firstname
        return super(ResPartner, self).copy(default)

    @api.multi
    def write(self, vals):
        vals = self._clean_names(vals)
        vals = self._precedence_check(vals)
        return super(ResPartner, self).write(vals)

    @api.model
    def create(self, vals):
        vals = self._clean_names(vals)
        vals = self._precedence_check(vals)
        return super(ResPartner, self).create(vals)

    @api.model
    def _install_partner_firstname(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("firstname", "=", False),
                               ("lastname", "=", False)])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d partners updated installing module.", len(records))


class ResCompany(models.Model):
    _inherit = 'res.company'

    names_order = fields.Selection(
        [('first_last', 'Firstname Lastname'),
         ('last_first', 'Lastname Firstname')],
        string="Names display order", default='last_first', required=True,
        help="Select order in which names are shown")

    @api.one
    def action_recalculate_names(self):
        partners = self.env['res.partner'].search([
            ('company_id', '=', self.id)
        ])
        _logger.info("Recalculating names for %d partners.", len(partners))
        partners._compute_name()
        _logger.info("%d partners updated.", len(partners))
        return True


class ResUsers(models.Model):
    _inherit = 'res.users'

    def copy(self, cr, uid, id, default=None, context=None):
        user2copy = self.read(
            cr, uid, [id], ['login', 'firstname', 'lastname'])[0]
        default = dict(default or {})
        if ('lastname' not in default) and ('partner_id' not in default):
            default['lastname'] = (_("%s (copy)") %
                                   user2copy['lastname'] or
                                   user2copy['firstname'])
        if 'login' not in default:
            default['login'] = _("%s (copy)") % user2copy['login']
        return super(ResUsers, self).copy(cr, uid, id, default, context)
