#Pre-requisite: Must have Python3 installed in the system
#1. Keep 'check_field.py' and 'taxonomy.json' in the folder where 'new_manual_run.sh' is present. 
#2. That's it. Run the new_manual_run.sh file exactly the way it was used before. 

#New Feature addition: 
#1. The field names which do not match the taxonomy will get printed out on console, and also, will be saved in a text file named 'unidentified_fields.txt'.
#2. If there are duplicate field names in any of the rules, the script will print out the error, with the rule-id in which there are duplicate field names. 

# TAKE CARE OF THE PARAMETERS ORDER!!!!! #
# MANDATORY
# 1: The master file. 
# 2: The logs file to be evaluated. 
# 3: The file where the results will be stored. 

#OPTIONAL
# 4: The file where the matching logs will be stored, default: matching_logs.txt
# 5: The file where the unmatching logs will be stored, default: unmatching_logs.txt

#Example
#  ./manual_run.sh G3master0407.xml logs2_tabs.txt logs2_results.txt &
# Use G3master0407.xml as master file, the logs2_tabs.txt file contains the logs to be evaluated and all results will be stored in logs2_results.txt file

#  ./manual_run.sh G3master0407.xml logs2_tabs.txt logs2_results.txt the_matchinglogs.log the_unmatchinglogs.log &
# Use G3master0407.xml as master file, the logs2_tabs.txt file contains the logs to be evaluated and all results will be stored in logs2_results.txt file, store the matching logs
# in the_matchinglogs.log file and unmatching logs in the_unmatchinglogs.log file

#NOTES
# Files with all results, the matching and unmatching logs results are truncated if the same file is specified.

if [[ -z $1 ]]
then
	echo "Rules/Logs/Output file missing. Please check."
	echo "Please provide your rules file as 1st argument, logs file as 2nd argument and output file as 3rd argument."
  exit 1
fi

if [[ -z $2 ]]
then
	echo "Rules/Logs/Output file missing. Please check."
	echo "Please provide your rules file as 1st argument, logs file as 2nd argument and output file as 3rd argument."
  exit 1
fi

if [[ -z $3 ]]
then
	echo "Rules/Logs/Output file missing. Please check."
	echo "Please provide your rules file as 1st argument, logs file as 2nd argument and output file as 3rd argument."
  exit 1
fi

if [[ -z $4 ]]
then
	matching_file="matching_logs.txt"
else
	matching_file=$4
fi

if [[ -z $5 ]]
then
	unmatching_file="unmatching_logs.txt"
else
	unmatching_file=$5
fi

#truncating files if input are the same
$(> $3)
$(> $matching_file)
$(> $unmatching_file)

#initialising the values of logs matched and logs unmatched. 
logs_matched=0
logs_unmatched=0

pdbtool=$(which pdbtool)
$pdbtool dictionary -p $1 > fields.txt

python3 check_field.py $1 fields.txt
ret=$?
if [ $ret -ne 0 ]
then
	exit 1
fi

rm fields.txt

while read line
do
  res=$($pdbtool match -P CTD -p $1 -M "$line" | tee -a $3 | grep .classifier.rule_id=)

  separator="-------------------------------------------------------------------------------------------------------------------------------------------------------------------"
  
  echo -e "$separator \n" | tee -a $3 > /dev/null
  if [[ $res == "" ]]
  then
     nomatch=$(cut -b 1-10000 <<< "$line") 
     unmatch="$nomatch"
     echo -e "$unmatch \n\n $separator \n" | tee -a $unmatching_file > /dev/null
     ((logs_unmatched++))
  else
     matchlog=$(cut -b 1-10000 <<< "$line")
     echo -e "$matchlog \n\n $separator \n" | tee -a $matching_file > /dev/null 
     ((logs_matched++))
  fi
done < <(cat $2)

echo "Logs matched:" $logs_matched
echo "Logs unmatched:" $logs_unmatched






