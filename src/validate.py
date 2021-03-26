'''
Created on 5 Feb 2021

@author: Chris Isbell

@copyright:  2021 CLEAR Project (UK Charity No. 1100602). All rights reserved.

@license:    Apache

@contact:    admin@clearproject.org.uk
'''

import sys
import csv
import time

from client import validationfields

class validate(object):
    '''
    classdocs
    '''


    def __init__(self, outpath, openmode="w"):
        '''
        Constructor
        '''
        self.outpath = outpath
        self.openmode = openmode

    def write(self, recs):
        """
        Write invalid client records to the output file (stdout if not specified) as CSV
        """
        with sys.stdout if self.outpath is None else open(self.outpath, self.openmode, newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
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
