# Run in terminal 'python fields_count.py -h' for help.

import os
import sys

import re
import argparse
from argparse import RawTextHelpFormatter

import xml.etree
from xml.etree import ElementTree as ET

#Create help function to be used as a help function for the script when run as 'python3 script.py -h'
parser = argparse.ArgumentParser(description=
("Objective: To give the count of fields used in a particular ruleset.\n"
"Instruction: It will prompt user for entering a ruleset name. Enter the ruleset you want field count of.\n"
"Output: It will print all the field names and their count in that ruleset." 
), 
formatter_class=RawTextHelpFormatter
)
parser.add_argument("[path/to/xml]") 

args = parser.parse_args()

def create_fields_list(str1):
    # Returns a list of fields in a rule.
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

def main():
	try:
		rule_file = sys.argv[1]
		if(os.stat(rule_file).st_size == 0):
			print('Empty rule file provided. Aborting...')
			exit (1)
	except IndexError:
		print('Rule file not provided. Please provide your rule file as your 1st argument.')
		exit (1)

	try:
		with open(rule_file,'rt') as f:
			global tree
			tree = ET.parse(f)
	except xml.etree.ElementTree.ParseError:
		print("Faulty rules file. Aborting...")
		exit (1)

	ruleset = input('Input ruleset: ')
	field_counts = {}

	for rulesets in tree.iter('ruleset'):
		if(rulesets.attrib['id']==ruleset):
			for rules in rulesets:
				for rule in rules:
					for pat_val in rule:
						if(pat_val.tag=='patterns'):
							for pattern in pat_val:
								pattern_text = pattern.text
								list_of_fields = create_fields_list(pattern_text)
								for field in list_of_fields:
									if field in field_counts:
										field_counts[field]+=1
									else:
										field_counts[field]=1
	
	if(len(field_counts)==0):
		print('This ruleset is not present in this rules file.')
		exit (1)

	print (field_counts)
	return 

if __name__ == "__main__":
  main()


