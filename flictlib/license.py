#!/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


import sys
import json

from license_expression import Licensing, LicenseSymbol

from flictlib.translator import read_translations
from flictlib.translator import update_license

from flictlib.relicense import read_relicense_file
from flictlib.relicense import relicense_license


#######################################################3

#
# debug and devel variable
#
LICENSE_DEBUG_VERBOSE=False
LICENSE_DEBUG=False

def enable_debug():
    set_debug(True)
    
def disable_debug():
    set_debug(False)

def set_debug(enabled):
    global LICENSE_DEBUG
    LICENSE_DEBUG=enabled

def license_debug(msg):
    if LICENSE_DEBUG:
        print(msg, file=sys.stderr)        
        
def license_verbose_debug(msg):
    if LICENSE_DEBUG_VERBOSE:
        license_expressions_debug(msg)


class ManagedLicenseExpression:
    """This class contains all the different transforms of a license
    expression. The member variables are:

    translated - "&" => "and", "GPLv2+" => "GPL-2-or-later"

    expanded   - relicensed, e.g. "LGPL-2.1-or-later" => "GPL-2.0-only")

    grouped    - "keithp-x11" => "Permissive"

    simplified - simplified (boolean algebra) "MIT and MIT" => "MIT"

    interim    - for internal use only

    set_list   - see interim_license_expression_set_list()

    """
    def __init__(self, license_expression):
        self.license_expression = license_expression
        self.expanded = []
        self.grouped = []
        self.translated = []
        self.simplified = []
        self.interim = []
        self.set_list = None

    def _debug_license(self, license_expression):
        license_debug("license expression:                    " + str(self.license_expression))
        license_debug("translated license expression:         " + str(self.translated))
        license_debug("expanded license expression:           " + str(self.expanded))
        license_debug("grouped license expression:            " + str(self.grouped))
        license_debug("simplified license expression:         " + str(self.simplified))
        _debug_interim_license_expression_list(self.interim)
        _debug_license_expression_set_list(self.set_list)

    def to_json(self):
        mle = {}
        mle['expanded']=self.expanded
        mle['grouped']=self.grouped
        mle['simplified']=self.simplified
        #print("set_list: " + str(self.set_list))
        mle['set_list']=self.set_list
        return mle

    
    
class LicenseExpressionList:
    def __init__(self, op, list):
        self.op = op
        self.list = list

class LicenseHandler:

    def __init__(self, translations_file, relicense_file, group_file):
        self.translations_file = translations_file
        self.translations = None
        self.relicense_file = relicense_file
        self.relicense_map = None
        self.group_file = group_file
        self.licensing = Licensing()

    
    def translate_and_relicense(self, license_expression):
        #print("translate_and_relicenseself: " + license_expression)
        transl = self.translate(license_expression)
        if transl == None or transl == "":
            transl = license_expression
        #print("translate_and_relicenseself: " + license_expression + " ==> " + transl)
        rel = self.expand_relicense(transl)
        if rel == None:
            rel = transl
        #print("translate_and_relicenseself: " + rel)
        return rel
        
        
    def expand_relicense(self, license_expression):
        if self.relicense_file != None and self.relicense_file != "":
            self.relicense_map = read_relicense_file(self.relicense_file)
            expanded = relicense_license(self.relicense_map, license_expression)
            return expanded.strip()
        else:
            return license_expression.strip()

    def group(self, license_expression):
        return license_expression.strip()

    def translate(self, license_expression):
        """If file name passed when creating object, this method will try
        to open it and make use of it. Otherwise the input is simply
        returned as output.
        """
        #print("translate \"" + license_expression + "\"")
        if self.translations_file != None and self.translations_file != "":
            if self.translations == None:
                self.translations = read_translations(self.translations_file)
            #print("translate \"" + license_expression + "\" => " + "\"" + update_license(self.translations, license_expression) + "\"")
            return str(update_license(self.translations, license_expression)).strip()
        else:
            return str(license_expression).strip()

    def simplify(self, license_expression):
        #print("simplify: \"" + license_expression + "\"")
        parsed = self.licensing._parse_and_simplify(license_expression)
        #print("parsed:     " + str(parsed))
        #print("simplified: " + str(parsed.simplify()))
        #return parsed.simplify()
        return parsed

    def license_expression_list_json(self, license_expression, relicense=True):
        license = self.license_expression_list(license_expression, relicense)
        output = {}
        output["license_expression"] = license_expression
        output["expanded"] = license.expanded
        output["grouped"] = license.grouped
        output["translated"] = license.translated
        output["simplified"] = license.simplified
        output["interim"] = license.interim
        output["set_list"] = license.set_list
        return output

        
    def license_expression_list(self, license_expression, relicense=True):

        license = ManagedLicenseExpression(license_expression)
        license.translated = self.translate(license_expression)
        #print("POPESCU #: " + self.translate(license_expression))
        #print("POPESCU #: " + license.translated)
        
        if relicense:
            license.expanded = self.expand_relicense(license.translated)
        else:
            license.expanded = license.translated
            
        license.grouped = self.group(license.expanded)

        # We need str to skip verbose output
        license.simplified = str(self.simplify(license.grouped))
        
        license.interim = self.interim_license_expression_list(license.simplified, self.licensing)
        
        license.set_list = self.interim_license_expression_set_list(license.interim)

        #print("TRANSLATED:.... " + str(license_expression) + " ----> " + str(license.set_list))
        #print("POPESCU i: " + license_expression)
        #print("POPESCU t: " + license.translated)
        #print("POPESCU e: " + license.expanded)
        #print("POPESCU g: " + license.grouped)
        #print("POPESCU s: " + license.simplified)
        ##print("POPESCU: " + str(license.interim))
        #print("POPESCU l: " + str(license.set_list))
        #print("")
        return license


    
    def interim_license_expression_list(self, license_expression, licensing):
        """
        Turns an expression like this:
            G AND (A OR B)
        into:
            AND [G, OR [A, B]]
        The latter is an interim format.
        """
        #print("")
        #print("parse(" + str(license_expression) + ")")
        tokenizer = licensing.get_advanced_tokenizer()
        tokenized = tokenizer.tokenize(str(license_expression))
        current_license=None
        current_licenses=[]
        current_op=None
        paren_expr = None
        paren_count=0
        for token in tokenized:
            tok = token.string
            if tok == '(':
                #print("(")
                if paren_expr == None:
                    paren_expr = ""
                else:
                    paren_expr = paren_expr + " " + tok
                    paren_count = paren_count + 1
            elif tok == ')':
                #print("about to parse: \"" + paren_expr + "\"  count: " + str(paren_count))
                if paren_count == 0:
                    current_license = self.interim_license_expression_list(paren_expr, licensing)
                    #print("got:            \"" + str(current_license) + "\"")
                    paren_expr=None
                else:
                    paren_count = paren_count - 1
                    paren_expr = paren_expr + " " + tok                
            elif tok == 'OR' or tok == 'AND':
                if paren_expr != None:
                    #print("TEMP " + tok)
                    paren_expr = paren_expr + " " + tok
                else:
                    #print("OPERATOR " + tok + " (" + str(current_op) + ")")
                    if current_licenses == None:
                        print("ERROR......")
                        print("ERROR......")
                        print("ERROR......")
                        exit(24)
                    if current_op == None:
                        # first operator
                        current_op = tok
                        #print("=cop: " + tok + "   " + current_license)
                        current_licenses.append(current_license)
                    elif current_op == tok:
                        # same operator
                        #print("-cop: " + tok + "   " + current_license)
                        current_licenses.append(current_license)
                    else:
                        # different operator
                        print("-------------------------------------------- Store me: " + current_op + " " + str(current_licenses))
                        exit(12)
            else:
                #print("tok: \"" + tok + "\"")
                if paren_expr != None:
                    #print("TEMP " + tok)
                    paren_expr = paren_expr + " " + tok
                else:
                    #print("license: " + tok)
                    current_license = tok

        current_licenses.append(current_license)
        if current_op == None:
            current_op = "AND"
        list = LicenseExpressionList(current_op, current_licenses)
        #print("DONE: " + str(license_expression) + " => " + str(list))
        return list

    def _combinations(self, lel):
        #print("lel : " + str(lel))
        if not isinstance(lel, LicenseExpressionList):
            return 1
        if lel.op == "AND":
            prod = 1
            for l in lel.list:
                prod = prod * _combinations(l)
            return prod
        elif lel.op == "OR":
            sum = 0
            for l in lel.list:
                sum = sum + _combinations(l)
            return sum
        else:
            print("ERROR: NO OP")
            exit(11)

    def interim_license_expression_set_list(self, interim_license_expression_list):
        """
        Turns an expression like this:
            AND [G, OR [A, B]]
        into:
            [ 
              { G, A },
              { G, B }
            ]
        The latter is an interim format.
        """    
        expanded_list=[]

        #print("Count: " + str(_combinations(interim_license_expression_list)))
        if not isinstance(interim_license_expression_list, LicenseExpressionList):
            # single license
            license_set= { interim_license_expression_list }
            expanded_list.append(list(license_set))
            license_verbose_debug("LEAF, returning " +  str(expanded_list))
            license_verbose_debug("cop: " + interim_license_expression_list )
            #print("managed____ \""  + str(expanded_list) + "\"  <---- MIDDLE")
            return expanded_list

        current_op = interim_license_expression_list.op;
        license_verbose_debug("cop: " + current_op )
        for lep in interim_license_expression_list.list:
            license_verbose_debug(" ------ lep ----- " + str(lep))
            if current_op == None:
                print("ERROR: NO OP")
                exit(11)

            elif current_op == "OR":
                lep_list = self.interim_license_expression_set_list(lep)
                expanded_list = self._manage_list_item_or(expanded_list, lep_list)

            elif current_op == "AND":
                lep_list = self.interim_license_expression_set_list(lep)
                expanded_list = self._manage_list_item_and(expanded_list, lep_list)
        #print("managed____ \""  + str(expanded_list) + "\"  <---- FINAL")
        return expanded_list

    def _manage_list_item_and(self, license_list, lep):
        license_verbose_debug(" * Andy" )
        if isinstance(lep, LicenseExpressionList):
            print(" -------------====== Andy ====-----------------" )
            exit(77)
            # TODO : implement below (for lep)
            print("AND Count 0: " + str(_combinations(lep)))
            for inner_lep in lep.list:
                print("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ AND Count A: " + str(_combinations(inner_lep)))
                set_list = self.interim_license_expression_set_list(inner_lep)
            return None
        else:
            # single license
            if len(license_list) == 0:
                license_verbose_debug("wooops: " + str(license_list))
                license_verbose_debug("wooops: " + str(lep))
                license_list = lep
            else:
                license_verbose_debug("daisy: " + str(license_list))
                license_verbose_debug("daisy: " + str(lep))
                license_verbose_debug(" -------------====== Andy ====----------------- SINGLE: " + str(license_list) )
                new_list=[]
                for item in license_list:
                    license_verbose_debug("  item: " + str(item) + " <--- "  + str(lep) )
                    for lep_item in lep:
                        license_verbose_debug("    item: " + str(item) + " <--- "  + str(lep_item) )
                        new_item =list(set(item + lep_item))
                        license_verbose_debug("    item: " + str(item)  )
                        new_list.append(new_item)
                    license_verbose_debug("    list: " + str(new_list)  )
                license_list = new_list
            return license_list


    def _manage_list_item_or(self, license_list, lep):
        license_verbose_debug(" * Orleans: " + (str(lep)))
        if isinstance(lep, LicenseExpressionList):
            # TODO : implement below (for lep)
            license_verbose_debug(" -------------====== ORLEANS ====----------------- : " + str(lep.license_list) )
            exit(77)
            for inner_lep in lep.license_list:
                print("        ====----------------- : " + str(inner_lep) )
                print("OR Count A: " + str(_combinations(inner_lep)))
                set_list = self.interim_license_expression_set_list(inner_lep)
                print("OR Count B: " + str(len(set_list)))
                license_list.append(inner_lep)
        else:
            # single license
            license_verbose_debug("HERE I AM .... \"" + str(lep) + "\"")
            if len(license_list) == 0:
                new_list=lep
                license_verbose_debug("topsss: " + str(license_list) + " size: " + str(len(license_list)))
                license_verbose_debug("topsss: " + str(lep) + " size: " + str(len(lep)))
                license_verbose_debug("topsss: " + str(new_list) + " size: " + str(len(new_list)))
            else:
                new_list = license_list
                license_verbose_debug("dapsss: " + str(license_list))
                license_verbose_debug("dappss: " + str(lep))
                for lep_item in lep:
                    license_verbose_debug("    item: " + str(license_list) + " <--- "  + str(lep_item) )
                    new_list.append(lep_item)

        return new_list

def _debug_license_expression_set_list(ilel):
    if not LICENSE_DEBUG:
        return
    print("interim license expression set list:  ", license_expression_set_list_to_string(ilel), file=sys.stderr)


def license_to_string_long(license):
    res = ""
    res = res + "original:   " + license.license_expression + "\n"
    res = res + "translated: " + license.translated + "\n"
    res = res + "expanded:   " + license.expanded + "\n"
    res = res + "simplified: " + license.simplified + "\n"
    res = res + "set_list:   " + str(license.set_list) + "\n"
    return res
    
def license_expression_set_list_to_string(set_list):
    string = "[ "
    first_set = True
    for license_set in set_list:
        if first_set:
            first_set = False
        else:
            string = string + ", "

        string = string + "{"
        first_item = True
        for item in sorted(license_set):
            if first_item:
                first_item = False
            else:
                string = string + ", "
            string = string + item
        string = string + "}"
    string = string + "]"
    return string

def _debug_interim_license_expression_list(lel):
    if not LICENSE_DEBUG:
        return
    #_debug_interim_license_expression_list_indent(lel, "")
    print("interim license expression list:       ", file=sys.stderr, end="")
    print(interim_license_expression_list_to_string(lel), file=sys.stderr)

def interim_license_expression_list_to_string(lel):
    if lel.op != None:
        op=lel.op
    else:
        op=""
    string = op + " ["
    first=True
    for item in lel.list:
        if first:
            first = False
        else:
            string = string + ", "
        if isinstance(item, LicenseExpressionList):
            string = string + interim_license_expression_list_to_string(item)
        else:
            string = string + item

    string = string + "]"
    return string

