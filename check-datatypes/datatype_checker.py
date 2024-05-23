# Run in terminal 'python datatype_checker.py -h' for help.

import sys

import re
import json
import argparse
from argparse import RawTextHelpFormatter

import xml.etree
from xml.etree import ElementTree as ET

#Create help function to be used with the script as python script.py -h
parser = argparse.ArgumentParser(description=
("Objective: To verify the datatype of field names written against the taxonomy.\n\n"
"Note:\n"
"\t1) Keep 'taxonomy.json' in the same directory as your script.\n"
"\t2) If you want warnings to be printed, remove '#' in line number 158 of script.\n\n"
"Result: Prints the 'ERROR' and 'Warning' on console.\n" 
"'ERROR' is when wrong parser is used. (For example, when @NUMBER used for a datatype of 'string'.)\n"
"'Warning' is when there is a data-format to be followed as mentioned in taxonomy. (For example, if data-format is event-time, a warning will be printed for the user to double check with the output.)\n"
), 
formatter_class=RawTextHelpFormatter
)
parser.add_argument("[path/to/your/xml/file]") 

args = parser.parse_args()

try:
	rule_file = sys.argv[1]
except IndexError:
	print('Please provide your rule file as its argument. Aborting...')
	exit (1)

def dict_map():
	# Mapping of conversion of parsers into datatypes. 
	parser_to_datatype = {}
	parser_to_datatype["@ESTRING"] = ['string','boolean']
	parser_to_datatype["@PCRE"] = 'string'
	parser_to_datatype["@NUMBER"] = ['number','integer']
	parser_to_datatype["@IPv4"] = 'ipv4' 
	parser_to_datatype["@IPv6"] = 'ipv6'
	parser_to_datatype["@MACADDR"] = 'mac'	
	parser_to_datatype["@FLOAT"] = ['number','integer']
	parser_to_datatype["@EMAIL"] = 'string'
	parser_to_datatype["@HOSTNAME"] = 'string'
	parser_to_datatype["@QSTRING"] = 'string'
	parser_to_datatype["@ANYSTRING"] = 'string'
	parser_to_datatype["@STRING"] = 'string'
	parser_to_datatype["@SET"] = 'string'
	return parser_to_datatype

def field_datatype_taxonomy_dict():
	# Returns a dictionary of format { field: { 
	#											'type':   
	#										    'format': 
	#														}}
	taxonomy_dict = {}
	try:
		with open('taxonomy.json', 'r') as f:
			dict = json.load(f)
	except FileNotFoundError:
		print('Error: The program could not find your \'taxonomy.json\' file.\nIf you have this file in any other directory, please go to line 40 of the script and give the correct path.\n')
		exit (1)
	
	for key in dict:
		if "format" in dict[key]:
			taxonomy_dict[key] = {'type':dict[key]['type'], 'format':dict[key]['format']}
		else:
			taxonomy_dict[key] = dict[key]['type']
	return taxonomy_dict

def extract_fieldtypes(str):
	# Extracts out the content between two '@'
	regex = "@[^@]*@"
	test_str = str
	return re.findall(regex,test_str)

def newrule_field_parser_dict(matches):
	# Returns a dictionary of format { field : parser }
	field_parser_dict = {}
	for i in range(0,len(matches)):
		x = matches[i].split(':')
		if(len(x)==1):
			continue
		if(x[1]!=""):
			parser = matches[i].split(':')[0]		
			field_parser_dict[matches[i].split(':')[1]] = parser
	return field_parser_dict

def newrule_field_datatype_dict(matches):
	# Returns a dictionary of format { field : datatype }
	field_datatype_dict = {}
	for i in range(0,len(matches)):
		x = matches[i].split(':')
		if(len(x)==1):
			continue
		if(x[1]!=""):
			field_type = matches[i].split(':')[0]		
			field_datatype_dict[matches[i].split(':')[1]] = parser_to_datatype[field_type] 
	return field_datatype_dict

def print_errors():
	# Prints all the errors on the console
	print("\n\n")
	for rule in tree.iter('rule'):
		for patterns in rule:
			for pattern in patterns:
				if(pattern.tag=='pattern'):
					ruletext = pattern.text
					global parser_to_datatype
					parser_to_datatype = dict_map()
					matches = extract_fieldtypes(ruletext)
					taxonomy = field_datatype_taxonomy_dict()
					created_parser_dict = newrule_field_parser_dict(matches)
					created_datatype_dict = newrule_field_datatype_dict(matches)
					for field in created_parser_dict:
						if(field not in taxonomy):
							continue
						if(created_datatype_dict[field]!=taxonomy[field]):
							if('format' not in taxonomy[field]):
								if(taxonomy[field] not in created_datatype_dict[field] and 'format' not in taxonomy[field]):
									print("ERROR: In rule-id: {}, incorrect parser used for field: {}, {} used while the datatype of this field in Taxonomy is: {}.".format(rule.attrib['id'],field,created_parser_dict[field],taxonomy[field]))
	print("\n\n")
	return 0

def print_warnings():
	# Prints all the warnings on the console
	for rule in tree.iter('rule'):
		for patterns in rule:
			for pattern in patterns:
				if(pattern.tag=='pattern'):
					ruletext = pattern.text
					matches = extract_fieldtypes(ruletext)
					taxonomy = field_datatype_taxonomy_dict()
					created_parser_dict = newrule_field_parser_dict(matches)
					created_datatype_dict = newrule_field_datatype_dict(matches)
					for field in created_parser_dict:
						if(field not in taxonomy):
							continue
						if(created_datatype_dict[field]!=taxonomy[field]):
							if('format' in taxonomy[field]):
								if(created_datatype_dict[field]!=taxonomy[field]['format'] and taxonomy[field]['format']!='domain' and taxonomy[field]['format']!='hostname' and taxonomy[field]['format']!='uri' and taxonomy[field]['format']!='path' and taxonomy[field]['format']!='email'):
										print ("Warning: In rule-id: {}, {} used for field: {}, but in taxonomy, data-type is: {} and data-format is: {}, please ensure output's value matches data-format.".format(rule.attrib['id'],created_parser_dict[field], field,taxonomy[field]['type'],taxonomy[field]['format']))
	print("\n\n")						
	return 0

def main():
	try:
		with open(rule_file,'rt') as f:
			global tree
			tree = ET.parse(f)
	except xml.etree.ElementTree.ParseError:
		print('There is some problem with your rules file. Aborting... ')
		exit (1)
	except FileNotFoundError:
		print('Rule file not found. Please check if you have given the right path and file name.')
		exit (1)

	print_errors()
	print_warnings()

	return 0

if __name__ == "__main__":
  main()






