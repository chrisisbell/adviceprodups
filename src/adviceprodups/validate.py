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
import time

from client import validationfields

class validate(object):
    '''
    classdocs
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
