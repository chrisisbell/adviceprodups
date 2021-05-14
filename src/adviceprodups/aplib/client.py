'''
Created on 5 Feb 2021

@author: Chris Isbell

@copyright:  2021 CLEAR Project (UK Charity No. 1100602). All rights reserved.

@license:    Apache

@contact:    admin@clearproject.org.uk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import unicodedata
import re
import datetime

__all__ = ["client", "validationfields"]

validationfields = ["System Client ID", "Agency Client Reference", "Field Name", "Invalid Value", "Reason", "No. Cases"]

def deaccent(strng):
    """
    Replace accented characters with their non-accented versions
    """
    return str(unicodedata.normalize('NFD', strng)\
           .encode('ascii', 'ignore')\
           .decode("utf-8"))
    
def tidyspaces(strng):
    """
    Replace multiple consecutive spaces in a string with a single space
    """
    return " ".join(strng.split())
    
genderdict = {"Male": "Male", "Female": "Female", "[Not Specified]": "unknown"}

# Regular expression to match National Insurance number
nimatch = re.compile("^[A-CEGHJ-PR-TW-Z]{1}[A-CEGHJ-NPR-TW-Z]{1}[0-9]{6}[A-DFM]{1}$")

# Regular expression to match Home Office reference number
horefmatch = re.compile("^[A-Z]{1}[0-9]{7}$")

# Regular expression to tidy mobile number (remove all non-digits)
mobilesub = re.compile("[^0-9]")

# Regular expression to validate email address
emailmatch = re.compile("^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$")

# Regular expression to validate post code
postcodematch = re.compile("[A-Z][A-HJ-Y]?[0-9]{1,2} ?[0-9][A-Z]{2}")

currentyear = datetime.date.today().year

class client(object):
    '''
    Internal representation of a client.
    
    A direct representation of a spreadsheet row, with some
    limited functionality for display and comparison. 
    '''

    def __init__(self, sysid, clientid, name, gender, ni, horef, mobile, email, postcode, dob, ncases=0):
        '''
        Constructor
        '''
        self.validationerrors = []
        self.ncases = ncases
        self.sysid = sysid
        self.clientid = clientid
        self.name = name
        self.gender = gender
        self.ni = ni
        self.horef = horef
        self.mobile = mobile
        self.email = email
        self.postcode = postcode
        self.dob = dob
     
    def __str__(self):
        """
        Summary of record
        """
        return "sysid: %d, clientid: %d, errors: %s" % (self.sysid, self.clientid, str(self.validationerrors))
        
    def __valerr(self, field, value, reason):
        self.validationerrors.append({"sysid": self.sysid, "cleintid": self.clientid, "field": field, "value": str(value), "reason": reason, "nocases": self.ncases})
        
        
    @property
    def isInvalid(self):
        """
        Returns True if this client has validation errors
        """
        return len(self.validationerrors) > 0

    @property
    def sysid(self):
        return self._sysid
    
    @sysid.setter    
    def sysid(self, sysid):
        try: 
            self._sysid=int(sysid)
            if self._sysid <= 0:
                raise ValueError("Out of range")            
        except ValueError as e:
            self._sysid=0
            self.__valerr("System Client ID", sysid, str(e)) 
    
    @property
    def clientid(self):
        return self._clientid
    
    @clientid.setter
    def clientid(self, clientid):
        try:
            if len(clientid) == 0:
                raise ValueError("No Client ID")
            self._clientid = int(clientid)
            if self._clientid <=0:
                raise ValueError("Out of range")            
        except ValueError as e:
            self._clientid=0
            self.__valerr("Agency Client Reference", clientid, str(e))
            
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        try:
            self._name = tidyspaces(deaccent(name).strip())
            if len(self._name) == 0:
                raise ValueError("Empty")
        except ValueError as e:
            self.__valerr("Client name", name, str(e))
    
    @property
    def searchname(self):
        """
        Returns the name as <given name> <family name>
        """
        l = self._name.split(", ")
        l.reverse()
        return " ".join(l)
        
            
    @property
    def gender(self):
        return self._gender
    
    @gender.setter
    def gender(self, gender):
        try:
            self._gender = genderdict[gender]
        except KeyError:
            self.__valerr("Gender", gender, "Not an allowed value")
            
    @property
    def ni(self):
        return self._ni
    
    @ni.setter
    def ni(self, ni):
        try:
            if ni is None:
                ni = ""
            self._ni = ni.strip().upper().replace(" ", "")
            if len(self._ni) == 0:
                return      # Empty - noting else to do
            if len(self._ni) != 9:
                raise ValueError("Invalid length")
            if not nimatch.match(self._ni):
                raise ValueError("Malformed")
        except ValueError as e:
            self.__valerr("NI Number", ni, str(e))
        
    @property
    def horef(self):
        return self._horef
    
    @horef.setter
    def horef(self, horef):
        try:
            if horef is None:
                horef = ""
            self._horef = horef.strip().upper().replace(" ", "")
            if len(self._horef) == 0:
                return
            if not horefmatch.match(self._horef):
                raise ValueError("Malformed")
        except ValueError as e:
            self.__valerr("Home Office Reference", horef, str(e))

    @property
    def mobile(self):
        return self._mobile
    
    @mobile.setter
    def mobile(self, mobile):
        try:
            if len(mobile) == 0:
                self._mobile = ""
                return
            if mobile.startswith("+44"):
                mobile = "0" + mobile[3:]
            self._mobile = mobilesub.sub("", mobile)
            if not self._mobile.startswith("0"):
                self._mobile = "0" + self._mobile
            if len(self._mobile) > 11:
                self._mobile = self._mobile[:11]
            if len(self._mobile) != 11:
                raise ValueError("Invalid length")
        except (ValueError, TypeError) as e:
            self.__valerr("Mobile Number", mobile, str(e))
            
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        try:
            self._email = email.strip().lower()
            if len(self._email) == 0:
                return 
            if not emailmatch.match(self._email):
                raise ValueError("Malformed")
        except ValueError as e:
            self.__valerr("Main E-Mail Address", email, str(e))

    @property
    def postcode(self):
        return self._postcode
    
    @postcode.setter
    def postcode(self, postcode):
        try:
            self._postcode = postcode.strip().upper()
            if len(self._postcode) == 0:
                return
            if not postcodematch.match(self._postcode):
                raise ValueError("Malformed")            
        except ValueError as e:
            self.__valerr("Postcode", postcode, str(e))

    @property
    def dob(self):
        return self._dob
    
    @dob.setter
    def dob(self, dob):
        try:
            self._dob = dob.strip()
            if len(self._dob) == 0:
                return
            dt = datetime.datetime.strptime(self._dob, "%d/%m/%Y")
            birthyear = dt.year
            age = currentyear - birthyear
            if age < 0 or age > 150:
                raise ValueError("Invalid age")
            # Assuming that the database has already validated this
        except (TypeError, ValueError) as e:
            self.__valerr("Date of Birth", dob, str(e))

    @property
    def ncases(self):
        return self._ncases
    
    @ncases.setter
    def ncases(self, ncases):
        try:
            self._ncases = int(ncases)
            if self._ncases < 0:
                raise ValueError("Out of range")
        except ValueError as e:
            self.__valerr("Number of Cases", ncases, str(e))


        