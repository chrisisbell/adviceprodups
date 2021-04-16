# encoding: utf-8
'''
apdups -- Detect duplicates in AdvicePro spreadsheet

apdups is a filter that reads a CSV table and flags possible duplicate entries

It defines classes_and_methods

@author:     Chris Isbell

@copyright:  2021 CLEAR Project (UK Charity No. 1100602). All rights reserved.

@license:    Apache

@contact:    admin@clearproject.org.uk
@deffield    updated: Updated

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

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from parseapcsv import parseapcsv
from validate import validate
from deduplicate import deduplicate

__all__ = ["main"]
__version__ = 0.1
__date__ = '2021-03-05'
__updated__ = '2021-03-16'

DEBUG = 0

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
        
        print("Validating", file=sys.stderr)
        validator = validate(args.output)
        validator.write(recs)
        
        print("Duplicate detection", file=sys.stderr)
        deduplicator = deduplicate(args.output)
        deduplicator.write(recs)
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
