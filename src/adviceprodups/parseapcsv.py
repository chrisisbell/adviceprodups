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

import csv
#from client import client

correctheader = ['System Client ID', 'Agency Client Reference', 'Surname, Forename', 'Gender', 'NI Number', 'Home Office Reference', 'Mobile Number', 'Main E-Mail Address', 'Postcode', 'Date of Birth', 'Number of Cases']

class parseapcsv(object):
    '''
    classdocs
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
        