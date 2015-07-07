# -*- coding: utf-8 -*-

# Authors: Nemry Jonathan
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# All Rights Reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contact a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from .base import BaseCase


class PartnerContactCase(BaseCase):
    def test_update_lastname(self):
        """Change lastname."""
        self.expect(u"newlästname", self.firstname)
        self.original.name = self.name

    def test_update_firstname(self):
        """Change firstname."""
        self.expect(self.lastname, u"newfïrstname")
        self.original.name = self.name

    def test_whitespace_cleanup(self):
        """Check that whitespace in name gets cleared."""
        self.expect(u"newlästname", u"newfïrstname")
        self.original.name = "  newlästname  newfïrstname  "

        # Need this to refresh the ``name`` field
        self.original.invalidate_cache()


class PartnerContactCaseInverse(PartnerContactCase):
    def test_copy(self):
        """Copy the partner and compare the result."""
        self.expect(u"%s (copy)" % self.firstname, self.lastname)
        self.changed = self.original.with_context(lang="en_US").copy()

    def create_original(self):
        super(PartnerContactCaseInverse, self).create_original()
        self.original.company_id.names_order = 'first_last'

    def expect(self, lastname, firstname, name=None):
        super(PartnerContactCaseInverse, self).expect(
            lastname, firstname, name)
        self.name = name or u"%s %s" % (firstname, lastname)

    def test_whitespace_cleanup(self):
        """Check that whitespace in name gets cleared."""
        self.expect(u"newlästname", u"newfïrstname")
        self.original.name = "  newfïrstname  newlästname  "

        # Need this to refresh the ``name`` field
        self.original.invalidate_cache()


class PartnerCompanyCase(BaseCase):
    def create_original(self):
        super(PartnerCompanyCase, self).create_original()
        self.original.is_company = True

    def test_copy(self):
        super(PartnerCompanyCase, self).test_copy()
        self.expect(self.name, False, self.name)

    def test_company_inverse(self):
        """Test the inverse method in a company record."""
        name = u"Thïs is a Companŷ"
        self.expect(name, False, name)
        self.original.name = name


class UserCase(PartnerContactCase):
    def create_original(self):
        self.original = self.env["res.users"].create({
            "name": u"%s %s" % (self.lastname, self.firstname),
            "login": "firstnametest@example.com"})
