#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

from flict.flictlib.format.json_format import JsonFormatter
from flict.flictlib.format.text_format import TextFormatter
from flict.flictlib.format.dot_format  import DotFormatter

class FormatFactory:

   _instance = None

   @staticmethod
   def formatter(format):
       if FormatFactory._instance is None:
           if format.lower() == "json":
               FormatFactory._instance = JsonFormatter()
           elif format.lower() == "text":
               FormatFactory._instance = TextFormatter()
           elif format.lower() == "dot":
               FormatFactory._instance = DotFormatter()
           elif format.lower() == "markdown":
               print("MARKDOWN COMING SOON: ")
           else:
               pass
       else:
           pass
       return FormatFactory._instance

        
