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
    def formatter(format_):
        if FormatterFactory._instance is None:
            if format_.lower() == "json":
                FormatterFactory._instance = JsonFormatter()
            elif format_.lower() == "text":
                FormatterFactory._instance = TextFormatter()
            elif format_.lower() == "dot":
                FormatterFactory._instance = DotFormatter()
            elif format_.lower() == "markdown":
                FormatterFactory._instance = PackageMarkdownFlictFormatter()
            # else ignored
        # else ignored
        return FormatterFactory._instance
