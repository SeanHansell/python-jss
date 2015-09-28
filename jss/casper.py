#!/usr/bin/env python
# Copyright (C) 2014, 2015 Shea G Craig <shea.craig@da.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""casper.py

Utility class for getting and presenting information from casper.jxml.

The results from casper.jxml are undocumented and thus quite likely to be
removed. Do not rely on its continued existence!
"""


import copy
import urllib
from xml.etree import ElementTree

from .tools import indent_xml


class Casper(ElementTree.Element):
    """Interact with the JSS through its private casper endpoint.

    The API user must have the Casper Admin privileges "Use Casper
    Admin" and "Save With Casper Admin".
    """

    def __init__(self, jss):
        """Initialize a Casper object.

        Args:
            jss: A JSS object to request the casper page from.
        """
        self.jss = jss
        self.url = "%s/casper.jxml" % self.jss.base_url
        self.auth = urllib.urlencode({"username": self.jss.user,
                                      "password": self.jss.password})
        super(Casper, self).__init__(tag="Casper")
        self.update()

    def __repr__(self):
        """Return a string with indented Casper data."""
        # deepcopy so we don't mess with the valid XML.
        pretty_data = copy.deepcopy(self)
        indent_xml(pretty_data)
        return ElementTree.tostring(pretty_data).encode("utf_8")

    def makeelement(self, tag, attrib):
        """Return an Element."""
        # We use ElementTree.SubElement() a lot. Unfortunately, it
        # relies on a super() call to its __class__.makeelement(), which
        # will fail due to the class NOT being Element. This handles
        # that issue.
        return ElementTree.Element(tag, attrib)

    def update(self):
        """Request an updated set of data from casper.jxml."""
        response = self.jss.session.post(self.url, data=self.auth)
        response_xml = ElementTree.fromstring(response.text.encode("utf_8"))

        # Remove previous data, if any, and then add in response's XML.
        self.clear()
        for child in response_xml.getchildren():
            self.append(child)
