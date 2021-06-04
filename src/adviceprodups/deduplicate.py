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

import sys
import csv
import inspect

from fuzzywuzzy import fuzz

#from client import validationfields

class deduplicate(object):
    '''
    classdocs
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
