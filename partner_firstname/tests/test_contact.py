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

from .base import BaseCase
from .. import exceptions as ex


class PartnerContactCase(BaseCase):
    def test_empty_names(self):
        """Create/update a contact with False/empty names."""
        cases = (
            (False, False),
            (False, ''),
            ('', False),
            ('', ''),
            ('  ', ''),
            ('', '   '),
            ('   ', '  ')
        )
        with self.assertRaises(ex.EmptyNamesError):
            for l, f in cases:
                self.next_case()
                self.partner_contact_create(l, f)
        self.changed = self.partner_contact_create(u"Lástnäme", u"Fírstnäme")
        with self.assertRaises(ex.EmptyNamesError):
            for l, f in cases:
                self.next_case()
                self.changed.write({'lastname': l, 'firstname': f})

    def test_only_firstname(self):
        """Create/update a contact with only firstname."""
        cases = (
            (False, u"Fírstnäme", u"Chängéd"),
            ('', u"Fírstnäme", u"Chängéd"),
            (False, u"Fírstnäme1 Fírstnäme2", u"Chängéd1 Chängéd2"),
            ('', u"Fírstnäme1 Fírstnäme2", u"Chängéd1 Chängéd2"),
            (u"Lástnäme", u"Fírstnäme", False),
            (u"Lástnäme", u"Fírstnäme", ''),
        )
        for l, f, fn in cases:
            self.next_case()
            self.changed = self.partner_contact_create(l, f)
            self.expect(l, f)
            self.changed.write({'firstname': fn})
            self.expect(l, fn)
        for l, f, fn in cases:
            self.next_case()
            with self.env.do_in_onchange():
                # User presses ``new``
                self.changed = self.new_partner(False)
                # User sets firstname, which triggers onchanges
                self.changed.firstname = f
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(False, f)
                # User changes firstname, which triggers onchanges
                self.changed.firstname = fn
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(False, fn)

    def test_only_lastname(self):
        """Create/update a contact with only lastname."""
        cases = (
            (False, u"Lástnäme", u"Chängéd"),
            ('', u"Lástnäme", u"Chängéd"),
            (False, u"Lástnäme1 Lástnäme2", u"Chängéd1 Chängéd2"),
            ('', u"Lástnäme1 Lástnäme2", u"Chängéd1 Chängéd2"),
            (u"Fírstnäme", u"Lástnäme", False),
            (u"Fírstnäme", u"Lástnäme", ''),
        )
        for f, l, ln in cases:
            self.next_case()
            self.changed = self.partner_contact_create(l, f)
            self.expect(l, f)
            self.changed.write({'lastname': ln})
            self.expect(ln, f)
        for f, l, ln in cases:
            self.next_case()
            with self.env.do_in_onchange():
                # User presses ``new``
                self.changed = self.new_partner(False)
                # User sets firstname, which triggers onchanges
                self.changed.lastname = l
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(l, False)
                # User changes firstname, which triggers onchanges
                self.changed.lastname = ln
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(ln, False)

    def test_names(self):
        """Create/update a contact with firstnames and lastnames."""
        cases = (
            (u"Fírstnäme", u"Lástnäme",
             u"FírstnämeChängéd", u"LástnämeChängéd"),
            (u"Fírstnäme1 Fírstnäme2", u"Lástnäme",
             u"Fírstnäme1 Fírstnäme2Chängéd", u"LástnämeChängéd"),
            (u"Fírstnäme", u"Lástnäme1 Lástnäme2",
             u"FírstnämeChängéd", u"Lástnäme1 Lástnäme2Chängéd"),
            (u"Fírstnäme1 Fírstnäme2", u"Lástnäme1 Lástnäme2",
             u"Fírstnäme1 Fírstnäme2Chängéd", u"Lástnäme1 Lástnäme2Chängéd"),
        )
        for f, l, fn, ln in cases:
            self.next_case()
            self.changed = self.partner_contact_create(l, f)
            self.expect(l, f)
            self.changed.write({'lastname': ln, 'firstname': fn})
            self.expect(ln, fn)
        for f, l, fn, ln in cases:
            self.next_case()
            with self.env.do_in_onchange():
                # User presses ``new``
                self.changed = self.new_partner(False)
                # User sets firstname, which triggers onchanges
                self.changed.firstname = f
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                # User sets lastname, which triggers onchanges
                self.changed.lastname = l
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(l, f)
                # User changes firstname, which triggers onchanges
                self.changed.firstname = fn
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                # User changes lastname, which triggers onchanges
                self.changed.lastname = ln
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(ln, fn)

    def test_whitespaces(self):
        """Create/update a contact with names with several whitespaces."""
        cases = (
            ("  F1   F2  ", "  L1   L2   ", u"F1 F2", u"L1 L2",
             "  C1   C2  ", "  D1   D2   ", u"C1 C2", u"D1 D2",),
            ("    ", "  L1   L2   ", u"", u"L1 L2",
             "  C1   C2  ", "     ", u"C1 C2", u"",),
            ("  F1   F2  ", "     ", u"F1 F2", u"",
             "    ", "  D1   D2   ", u"", u"D1 D2",),
        )
        for f, l, fc, lc, fn, ln, fnc, lnc in cases:
            self.next_case()
            self.changed = self.partner_contact_create(l, f)
            self.expect(lc, fc)
            self.changed.write({'lastname': ln, 'firstname': fn})
            self.expect(lnc, fnc)
        for f, l, fc, lc, fn, ln, fnc, lnc in cases:
            self.next_case()
            with self.env.do_in_onchange():
                # User presses ``new``
                self.changed = self.new_partner(False)
                # User sets firstname, which triggers onchanges
                self.changed.firstname = f
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                # User sets lastname, which triggers onchanges
                self.changed.lastname = l
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(lc, fc)
                # User changes firstname, which triggers onchanges
                self.changed.firstname = fn
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                # User changes lastname, which triggers onchanges
                self.changed.lastname = ln
                self.changed._onchange_subnames()
                self.changed._onchange_name()
                self.expect(lnc, fnc)

    def test_copy(self):
        """Copy a contact."""
        cases = (
            (u"Fírstnäme", u"Lástnäme",
             u"Fírstnäme (copy)", u"Lástnäme"),
            (u"Fírstnäme1 Fírstnäme2", u"Lástnäme",
             u"Fírstnäme1 Fírstnäme2 (copy)", u"Lástnäme"),
            ("", u"Lástnäme",
             u"(copy)", u"Lástnäme"),
            ("  ", u"Lástnäme",
             u"(copy)", u"Lástnäme"),
            (False, u"Lástnäme",
             u"(copy)", u"Lástnäme"),
            (u"Fírstnäme", u"",
             u"(copy)", u"Fírstnäme"),
            (u"Fírstnäme", u"  ",
             u"(copy)", u"Fírstnäme"),
            (u"Fírstnäme1 Fírstnäme2", "",
             u"Fírstnäme2 (copy)", u"Fírstnäme1"),
            (u"Fírstnäme1 Fírstnäme2", "  ",
             u"Fírstnäme2 (copy)", u"Fírstnäme1"),
            (u"Fírstnäme1 Fírstnäme2", False,
             u"Fírstnäme2 (copy)", u"Fírstnäme1"),
        )
        for f, l, fc, lc in cases:
            self.next_case()
            self.changed = self.partner_contact_create(l, f)
            self.expect(l, f)
            self.changed = self.original.with_context(lang="en_US").copy()
            self.expect(lc, fc)


class UserContactCase(PartnerContactCase):
    def partner_contact_create(self, lastname, firstname):
        return self.user_create(lastname, firstname)


class PartnerContactCaseInverse(PartnerContactCase):
    def setUp(self):
        super(PartnerContactCaseInverse, self).setUp()
        self.company.names_order = 'first_last'

    def _join_names(self, lastname, firstname):
        return super(PartnerContactCaseInverse, self)._join_names(
            firstname, lastname)

    def test_copy(self):
        """Copy a contact."""
        cases = (
            (u"Fírstnäme", u"Lástnäme",
             u"Fírstnäme", u"Lástnäme (copy)"),
            (u"Fírstnäme1 Fírstnäme2", u"Lástnäme",
             u"Fírstnäme1", u"Fírstnäme2 Lástnäme (copy)"),
            ("", u"Lástnäme",
             u"Lástnäme", u"(copy)"),
            ("  ", u"Lástnäme",
             u"Lástnäme", u"(copy)"),
            (False, u"Lástnäme",
             u"Lástnäme", u"(copy)"),
            (u"Fírstnäme", u"",
             u"Fírstnäme", u"(copy)"),
            (u"Fírstnäme", u"  ",
             u"Fírstnäme", u"(copy)"),
            (u"Fírstnäme1 Fírstnäme2", "",
             u"Fírstnäme1", u"Fírstnäme2 (copy)"),
            (u"Fírstnäme1 Fírstnäme2", "  ",
             u"Fírstnäme1", u"Fírstnäme2 (copy)"),
            (u"Fírstnäme1 Fírstnäme2", False,
             u"Fírstnäme1", u"Fírstnäme2 (copy)"),
        )
        for f, l, fc, lc in cases:
            self.next_case()
            self.changed = self.partner_contact_create(l, f)
            self.expect(l, f)
            self.changed = self.original.with_context(lang="en_US").copy()
            self.expect(lc, fc)
