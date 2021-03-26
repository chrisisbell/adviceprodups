#!/usr/bin/env python3
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
'''

import sys
import os
import time

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from parseapcsv import parseapcsv
from validate import validate
from deduplicate import deduplicate

__all__ = []
__version__ = 0.1
__date__ = '2021-02-05'
__updated__ = '2021-02-19'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

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
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
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
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + str(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'apdups_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())