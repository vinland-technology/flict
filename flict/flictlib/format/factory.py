#!/usr/bin/env python3

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
from flict.flictlib.format.dot_format import DotFormatter
from flict.flictlib.format.markdown_format import PackageMarkdownFlictFormatter


class FormatterFactory:

    _instance = None

    @staticmethod
    def formatter(format):
        if FormatterFactory._instance is None:
            if format.lower() == "json":
                FormatterFactory._instance = JsonFormatter()
            elif format.lower() == "text":
                FormatterFactory._instance = TextFormatter()
            elif format.lower() == "dot":
                FormatterFactory._instance = DotFormatter()
            elif format.lower() == "markdown":
                FormatterFactory._instance = PackageMarkdownFlictFormatter()
            else:
                pass
        else:
            pass
        return FormatterFactory._instance
