"""
Exception classes of WPS
"""
# Author:	Jachym Cepicky
#        	http://les-ejk.cz
# Lince:
#
# Web Processing Service implementation
# Copyright (C) 2006 Jachym Cepicky
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from xml.dom.minidom import Document
from pywps.Soap import SOAP
import pywps.Soap
import sys

called = 0


class WPSException(Exception):
    """
    WPSException should be base class for all exceptions
    """
    code = "NoApplicableCode"
    value = None
    locator = None

    def promoteException(self,contentType = False, toFiles=None):
        """Print this exception text to files

        Parameters:
        toFiles {List} list of file objects, where to put  this exception
            text. Default. sys.stdout && sys.stderr
        """

        if toFiles:
            for i in toFiles:
                if contentType: print >>i, "Content-type: text/xml\n"
                print >>i, self
        else:
            if contentType: print >>sys.stdout, "Content-type: text/xml\n"
            print >>sys.stdout, self

    def _make_xml(self):
        # formulate XML
        self.document = Document()
        self.ExceptionReport = self.document.createElementNS("http://www.opengis.net/ows","ExceptionReport")
        self.ExceptionReport.setAttribute("xmlns","http://www.opengis.net/ows")
        self.ExceptionReport.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")
        self.ExceptionReport.setAttribute("version","1.0.0")
        self.document.appendChild(self.ExceptionReport)

        # make exception

        self.Exception = self.document.createElement("Exception")
        self.Exception.setAttribute("exceptionCode",self.code)

        if self.locator:
            self.Exception.setAttribute("locator",self.locator)

        self.ExceptionReport.appendChild(self.Exception)
        #self.value = None

    def __str__(self):

        response= self.document.toprettyxml(indent='\t', newl='\n', encoding="utf-8")
        if pywps.Soap.soap == True:
            soapCls = SOAP()
            response = soapCls.getResponse(response)

        sys.stderr.write("PyWPS %s: Locator: %s; Value: %s\n" % (self.code, self.locator, self.value))

        return response

class MissingParameterValue(WPSException):
    def __init__(self, value):
        self.code = "MissingParameterValue"
        self.locator = str(value)
        self._make_xml()

class InvalidParameterValue(WPSException):
    def __init__(self,value):
        self.code = "InvalidParameterValue"
        self.locator = str(value)
        self._make_xml()

class NoApplicableCode(WPSException):
    def __init__(self,value=None):
        WPSException.__init__(self,value)
        self.code = "NoApplicableCode"
        self.value = None
        self._make_xml()
        self.message = value
        if value:
            self.ExceptionText = self.document.createElement("ExceptionText")
            self.ExceptionText.appendChild(self.document.createTextNode(value))
            self.Exception.appendChild(self.ExceptionText)
            self.value = str(value)

class VersionNegotiationFailed(WPSException):
    def __init__(self,value=None):
        self.code = "VersionNegotiationFailed"
        self.locator = None
        self._make_xml()
        if value:
            self.ExceptionText = self.document.createElement("ExceptionText")
            self.ExceptionText.appendChild(self.document.createTextNode(value))
            self.Exception.appendChild(self.ExceptionText)
            self.value = str(value)

class NotEnoughStorage(WPSException):
    def __init__(self,value=None):
        self.code = "NotEnoughStorage"
        self.locator = value
        self._make_xml()

class StorageNotSupported(WPSException):
    def __init__(self,value=None):
        self.code = "StorageNotSupported"
        self.locator = value
        self._make_xml()

class ServerBusy(WPSException):
    def __init__(self,value=None):
        self.code = "ServerBusy"
        self.value = value
        self._make_xml()

class FileSizeExceeded(WPSException):
    def __init__(self,value=None):
        self.code = "FileSizeExceeded"
        self.locator = str(value)
        self._make_xml()

class ServerError(WPSException):
    def __init__(self,value=None):
        raise NoApplicableCode(value)
        self.code = "ServerError"
        try:
            self.locator = str(value)
        except:
            self.locator = None
        self._make_xml()
        self.ExceptionText = self.document.createElement("ExceptionText")
        self.ExceptionText.appendChild(self.document.createTextNode("General server error"))
        self.Exception.appendChild(self.ExceptionText)

