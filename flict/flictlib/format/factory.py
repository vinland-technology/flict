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

    @staticmethod
    def formatter(format_):
        if format_.lower() == "text":
            return TextFormatter()
        elif format_.lower() == "dot":
            return DotFormatter()
        elif format_.lower() == "markdown":
            return PackageMarkdownFlictFormatter()
        return JsonFormatter()
