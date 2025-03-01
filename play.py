#!/usr/bin/python3
import sys
import re
import requests
import csv
import pandas as pd
from io import StringIO
from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

header = [
    'Email',
    'Contact Name',
    'Phone Number',
    'Residence Name',
    'Organization Name',
    'Stage',
    'Location',
    'County',
    'NARR Level',
    'Cert Date or Last Contact Date',
    'Interviewer',
    'unused',
    'Notes',
    'System Notes'
]

unused = [
          '',
          '\0',
          'DEPARTMENT OF HEALTH SERVICES',
          'Division of Quality Assurance',
          'STATE OF WISCONSIN',
          'Bureau of Health Services',
          'PO Box 2969',
          'Madison, WI 53701-2969',
          'Recovery Residence Registry',
          'By County, City, and Name'
          ]

beginning = [
          'Updated',
          'Page ',
          'Certified by: ',
          'Maximum Num',
          'Allows Medica',
          'Registered Date'
]

counties = [
    'ADAMS',
    'ASHLAND',
    'BARRON',
    'BAYFIELD',
    'BROWN',
    'BUFFALO',
    'BURNETT',
    'CALUMET',
    'CHIPPEWA',
    'CLARK',
    'COLUMBIA',
    'CRAWFORD',
    'DANE',
    'DODGE',
    'DOOR',
    'DOUGLAS',
    'DUNN',
    'EAU CLAIRE',
    'FLORENCE',
    'FOND DU LAC',
    'FOREST',
    'GRANT',
    'GREEN',
    'GREEN LAKE',
    'IOWA',
    'IRON',
    'JACKSON',
    'JEFFERSON',
    'JUNEAU',
    'KENOSHA',
    'KEWAUNEE',
    'LA CROSSE',
    'LAFAYETTE',
    'LANGLADE',
    'LINCOLN',
    'MANITOWOC',
    'MARATHON',
    'MARINETTE',
    'MARQUETTE',
    'MENOMINEE',
    'MILWAUKEE',
    'MONROE',
    'OCONTO',
    'ONEIDA',
    'OUTAGAMIE',
    'OZAUKEE',
    'PEPIN',
    'PIERCE',
    'POLK',
    'PORTAGE',
    'PRICE',
    'RACINE',
    'RICHLAND',
    'ROCK',
    'RUSK',
    'SAUK',
    'SAWYER',
    'SHAWANO',
    'SHEBOYGAN',
    'SAINT CROIX',
    'TAYLOR',
    'TREMPEALEAU',
    'VERNON',
    'VILAS',
    'WALWORTH',
    'WASHBURN',
    'WASHINGTON',
    'WAUKESHA',
    'WAUPACA',
    'WAUSHARA',
    'WINNEBAGO',
    'WOOD'
]

flags = [
    'Updated: ',
    'Deleted'
]

operated_string = 'Operated by: '
contact_string = 'Contact: '
url = 'https://www.dhs.wisconsin.gov/guide/recovresdir.pdf'


# main
def main():
    online = False
    oldPDF = 'recovresdir.pdf'

    text = StringIO()
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, text, laparams=LAParams(line_margin=7))
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    with open(oldPDF, 'rb') as db:
        for page in PDFPage.get_pages(db):
            interpreter.process_page(page)
    
    data = parsePDF(text.getvalue())
    toCSV('out15.csv', data)
    return
    
def toCSV(outfile, data_list):
    with open(outfile, 'w') as outfile:
        output = ''
        for row in data_list:
            for elt in row:
                if (',' in elt):
                    elt = f'\"{elt}\"'
                output += f'{elt},'
            output = output[:-1]
            output += '\n'

        outfile.write(output)
    outfile.close()
        
    return



def parsePDF(text):
    every_line = re.split('\\0|\\n|\\r|\\x0c', text)
    every_line = [x for x in every_line if x not in unused 
                                        and not x.strip().isnumeric()
                                        and not any(x.startswith(b) for b in beginning)]

    email = ''
    contact_name = ''
    phone = ''
    residence_name = ''
    orgName = ''
    location = ''
    county = every_line[0]
    final = list()

    every_line.append('') # for iter purposes

    for i in range(1, len(every_line) - 1):
        elt = every_line[i]

        if (isOrg(elt)):
            if (orgName): # not enough fulfillments to push everything
                final.append([email, contact_name, phone, residence_name, orgName, '', location, county, '', '', '', '', '', ''])
                email = ''
                contact_name = ''
                phone = ''
                residence_name = ''
                orgName = ''
                location = ''

            residence_name = every_line[i - 1] # NOT GUARANTEED !
            orgName = elt[len(operated_string):]
            email = ''
            contact_name = ''
            phone = ''
            location = ''
        elif (isPhone(elt)):
            phone = elt
            if (isEmail(every_line[i + 1])):
                email = every_line[i + 1]  # NOT GUARANTEED !
        elif (isLocation(elt)):
            location = elt[:elt.find(',')].upper()
            first_occurence = every_line.index(location) # UNCHECKED
            if (isCounty(every_line[first_occurence - 1])):
                county = every_line[first_occurence - 1]
            elif (isCounty(location)):
                county = location
        if (isContact(elt)):
            contact_name = elt[elt.index(contact_string) + len(contact_string):]
        

        if (contact_name and phone and residence_name and orgName and location):
            final.append([email, contact_name, phone, residence_name, orgName, '', location, county, '', '', '', '', '', ''])
            email = ''
            contact_name = ''
            phone = ''
            residence_name = ''
            orgName = ''
            location = ''
    
    return final

def isPhone(elt):
    return elt[0] == '(' and elt[1:4].isnumeric() and elt[4] == ')' and '-' in elt

def isLocation(elt):
    return ', WI' in elt and elt[-5:].isnumeric()

def isOrg(elt):
    return elt.startswith(operated_string)

def isCounty(elt):
    return elt in counties

def isEmail(elt):
    return ('@' in elt or 'www.' in elt 
            or '.com' in elt or '.gov' in elt 
            or '.net' in elt or '.org' in elt)

def isContact(elt):
    return contact_string in elt
  
    

if __name__ == '__main__': sys.exit(main())
