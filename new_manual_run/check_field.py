"""
Helper script for the other script 'new_manual_run.sh'.
Functionality:
1. Checks unidentified fields against our taxonomy. 
2. Checks if there are any any duplicate fields in any rule. 
"""
import os
import sys
import subprocess

import json
import re

import xml.etree
from xml.etree import ElementTree

def get_taxonomy_field_names():
	# Helper function for function 'check_unidentified_fields'.
	# Returns a list of field names in our taxonomy. Uses ''taxonomy.json' file. 		
	try:
		with open('taxonomy.json', 'r') as f:
			taxonomy = json.load(f)
	except FileNotFoundError:
		print('The program could not find your \'taxonomy.json\' file. If present in any other directory, please update the path in \'check_field.py\'.')
		sys.exit(1)
	taxonomy_list = []
	for field in taxonomy:
		taxonomy_list.append(field)
	return taxonomy_list

def check_unidentified_fields():
	# Checks if there are any unidentified field names present in the rules. 
	taxonomy_list = get_taxonomy_field_names()
	unidentified_fields = set()
	for field in fields_list:
		if (field.startswith('tmp')):
			# Ignoring field names staring with 'tmp', because they are used to merge the final values into a recognised taxonomy field. 
		    continue
		if field in taxonomy_list:
		    continue
		else:
		    unidentified_fields.add(field)
	print_unidentified_fields_and_write_to_file(unidentified_fields)
        
def print_unidentified_fields_and_write_to_file(unidentified_fields):
	# Prints unidentified fields and writes to a file.
	if(len(unidentified_fields)>0):
		# Prints out unidentified fields on console. 
		print("\nFound field names which did not match with the taxonomy.")
		print (unidentified_fields)
		print("\n") 
		file = open("unidentified_fields.txt","w")
		file.write('\n')
		for unidentified_field in unidentified_fields:
		    file.write(unidentified_field)
		    file.write(' ')
		file.write('\n\n')
		file.close()
		return 0		
		
def create_fields_list(str1):
	# Helper for 'print_duplicate fields'.
    # Returns list of field names written in a rule. 
    regex = "@[^@]*@"
    test_str = str1
    matches = re.findall(regex,test_str)
    list_of_fields = []
    for i in range(0,len(matches)):
        x = matches[i].split(':')
        if(len(x)==1):
            continue
        if(x[1]!=""):
            list_of_fields.append(x[1])
    return list_of_fields
    
def validate_xml():
	#Validates the xml against our patterndb.xsd
	try:
		p = subprocess.check_output('xmllint --schema patterndb.xsd {} --noout'.format(rule_file),shell=True)
	except Exception:
		print ('\nYour rules file does not follow the proper xml structure that FireEye uses. Please check again and rectify. \nExiting.\n')
		exit (1)
	
def print_duplicate_fields():
	# Prints to console if there are any duplicate field names in the rules. 
	try:
		with open(rule_file,'rt') as f:
			tree = ElementTree.parse(f)
	except xml.etree.ElementTree.ParseError:
		print ('Error: Faulty rules file. Aborting...')
		sys.exit(1)
	#Creating a dictionary as {'ruleid':'pattern'}
	ruleid_pat_dict = {}
	for rule in tree.iter('rule'):
		for pat_val in rule:
		    if(pat_val.tag=='patterns'):
		        for pattern in pat_val:
		            ruleid_pat_dict[rule.attrib['id']]=pattern.text
	#Iterating through each pattern in dict to find any duplicates.  
	for rule in ruleid_pat_dict:
		pattern = ruleid_pat_dict[rule]
		list_of_fields = create_fields_list(pattern)
		fields_set = set(list_of_fields)
		if(len(list_of_fields)!=len(fields_set)):
		    print("Duplicate field names found in rule-id: "+rule)
	print("\n")     
	return 0

def main():
	global rule_file
	rule_file = sys.argv[1]
	
	global field_file
	field_file = sys.argv[2]
	
	with open(field_file) as f:
		global fields_list
		fields_list = list(f)

	fields_list = [field.rstrip('\n') for field in fields_list]
	
	validate_xml()
	#Validate if the xml structure used is correct. 

	check_unidentified_fields()
	#Check if there are any unidentified fields in the rules. 

	print_duplicate_fields()
	#Check of there are any duplicate fields in any rule.

if __name__ == "__main__":
  main()
