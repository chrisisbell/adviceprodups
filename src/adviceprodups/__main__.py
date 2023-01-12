#!/usr/bin/env python3
'''
Created on 16 Mar 2021

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

import sys
import os
import time
import unicodedata
import re
import datetime
import csv

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from fuzzywuzzy import fuzz

correctheader = ['System Client ID', 'Agency Client Reference', 'Surname, Forename', 'Gender', 'NI Number', 'Home Office Reference', 'Mobile Number', 'Main E-Mail Address', 'Postcode', 'Date of Birth', 'Number of Cases']
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

class validate(object):
    '''
    Class to write a validation report to a CSV file
    '''

    def __init__(self, fp):
        '''
        Constructor
        '''
        self.fp = fp

    def write(self, recs):
        """
        Write invalid client records to the output file (stdout if not specified) as CSV
        """
        writer = csv.writer(self.fp, quoting=csv.QUOTE_NONNUMERIC)
        # Write headers
        writer.writerow(["Report generated", time.strftime("%d-%b-%Y %H:%M")])
        # Count number of clients with validation errors
        reccount = 0
        for client in recs:
            if client.isInvalid:
                reccount += 1
        writer.writerow(["Validation errors", reccount, "No. records", len(recs)])
        writer.writerow([])
        if reccount == 0:
            return      # No validation error records to write
        
        writer.writerow(validationfields)
        for client in recs:
            if client.isInvalid:
                for e in client.validationerrors:
                    writer.writerow(e.values())

class deduplicate(object):
    '''
    Class to write a suspected duplicates report to a CSV file
    '''

    def __init__(self ,fp):
        '''
        Constructor
        '''
        self.fp = fp
        self.dups = {}
        self.fuzzycount = 0
        
    def write(self, recs):
        """
        Write duplicate client records to the output file (sdtout if not specified) as CSV
        """
        writer = csv.writer(self.fp, quoting=csv.QUOTE_NONNUMERIC)
        # Write headers           
        writer.writerow([])
        writer.writerow(["Possible duplicates"])
        writer.writerow([validationfields[0] + " 1", validationfields[1] + " 1", validationfields[0] + " 2", validationfields[1] + " 2", validationfields[5] + " 1", validationfields[5] + " 2", "Score", "Reasons"])
        for i in range(0, len(recs) - 1):
            target = recs[i]
            for j in range(i + 1, len(recs)):
                cand = recs[j]
                score, reasons = self.similarity(cand, target)
                if score >= 0.3:
                    writer.writerow([target.sysid, target.clientid, cand.sysid, cand.clientid, target.ncases, cand.ncases, int(score * 100), ", ".join(reasons)])
                    #print(int(score * 100), '"' + cand.name + '"' , '"' +target.name + '"', reasons)
        print("No. of fuzzy matches", self.fuzzycount, file=sys.stderr)
            
    def similarity(self, a, b):
        """
        Produce a similarity metric with reasons for two candidate records.
        
        Returns the similarity score in the range 0.0 to 1.0 and an array
        of strings detailing the reasons for the match.
        """
        reasons = []
        if a.gender != b.gender and a.gender != "unknown":
            return 0.0, []   # Different genders - almost certainly not a duplicate

        # Get out quickly if unchangeable fields are present and different
        if a.ni != b.ni and len(a.ni) != 0:
            return 0.0, []
        if a.horef != b.horef and len(a.horef) != 0:
            return 0.0, []
        if a.dob != b.dob and len(a.dob) != 0:
            return 0.0, []
        
        # Distinct identifiers
        acrmatch =  a.clientid == b.clientid
        nimatch = a.ni == b.ni and len(a.ni) != 0
        horefmatch = a.horef == b.horef and len(a.horef) != 0
        if acrmatch:
            reasons.append("Agency Client Reference")
        if nimatch:
            reasons.append("NI number")
        if horefmatch:
            reasons.append("Home Office reference")
        if acrmatch or nimatch or horefmatch:
            return 1.0, reasons
        # Confirmatory identifiers
        cmatches = 0
        if a.mobile == b.mobile and len(a.mobile) != 0:
            cmatches += 8
            reasons.append("Mobile number")
        if a.email == b.email and len(a.email) != 0:
            cmatches += 8
            reasons.append("Email")
        if a.dob == b.dob and len(a.dob) != 0 and not a.dob.startswith("01/01"):
            # Ignore date of birth if 1st January. This is used when only the year is known.
            cmatches += 1
            reasons.append("Date of birth")
        if a.postcode == b.postcode and len(a.postcode) != 0:
            cmatches += 1
            reasons.append("Postcode")
        
        if cmatches > 2:
            if cmatches > 10:
                cmatches = 10
            return cmatches / 10.0, reasons
        
        # Only perform expensive fuzzy name comparison if necessary
        score = fuzz.token_sort_ratio(a.searchname, b.searchname)
        self.fuzzycount += 1
        #if score >= 65:
        #    print(score, ',', a.clientid, ',', b.clientid, ',"' + a.searchname + '","' + b.searchname + '",', 1 if score * (cmatches + 1) / 300. > 0.32 else 0, ",", score * (cmatches + 1) / 300.)
        reasons.append("Name")
        return score * (cmatches + 1) / 300., reasons

class parseapcsv(object):
    '''
    Class to parse the CSV input from the AdvicePro report generator and produce an array of client records
    '''


    def __init__(self, filename):
        '''
        Constructor
        '''
        self.records = []
        self.filename = filename
 
    def readall(self):
        """
        Read all records - ignoring the header record
        """
        with open(self.filename, newline="") as r:
            csvr = csv.reader(r)
            header = next(csvr, None)    # Skip header row
            if header != correctheader:
                raise ValueError("Spreadsheet header row incorrect")
                
            for row in csvr:
                self.records.append(client(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
                
        return self.records        

__version__ = 0.1
__date__ = '2021-03-05'
__updated__ = '2021-03-16'

DEBUG = 1

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    start_cpu = time.process_time()
    start_real = time.time()
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "Detect duplicates in AdvicePro spreadsheet"
    program_license = '''%s

  Created by Chris Isbell on %s.
  Copyright 2021 CLEAR Project (UK Charity No. 1100602). All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        argparser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        argparser.add_argument('-v', '--version', action='version', version=program_version_message)
        argparser.add_argument('-o', '--output',  help="path to output file")
        argparser.add_argument(dest="path", help="path to file containing the raw data [default: %(default)s]", metavar="CSV export file from AdvicePro")

        # Process arguments
        args = argparser.parse_args()
        
        print("Reading input", file=sys.stderr)
        parser = parseapcsv(args.path)
        recs = parser.readall()
            
        f = sys.stdout if args.output is None else open(args.output, 'w', newline='')
        try:            
            print("Validating", file=sys.stderr)
            validator = validate(f)
            validator.write(recs)
            
            print("Duplicate detection", file=sys.stderr)
            deduplicator = deduplicate(f)
            deduplicator.write(recs)
        finally:
            if f != sys.stdout:
                f.close()
            
        end_cpu = time.process_time()
        end_real = time.time()
        print("Completed in %4g CPU seconds and %4g clock seconds" % (end_cpu - start_cpu, end_real - start_real), file=sys.stderr)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG :
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + str(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == '__main__':
    sys.exit(main())
