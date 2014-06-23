# Created on Oct 3rd, 2013
# Refactored on Oct 11, 2013 to include grade and country
# @author: Sherwin Wu for ALFA, MIT lab: sherwu@mit.edu
# @author: Colin Taylor, colin_t@mit.edu
# =============================
# IMPORTANT!!!
# This script requires a file called 'percent_duration_by_user_grade.csv' or 'total_duration_by_user_grade.csv'
# and will output a file called 'duration_aggregate_by_grade.csv' and 'duration_aggregate_by_country.csv'
# =============================
import json
import csv

# Use collections.defaultdict
def initialize_dict(types):
	temp_dict = {}
	for type1 in types:
		temp_dict[type1] = 0
	return temp_dict


def initialize_variable_dict(aggregate_variables, resource_types):
	counts = initialize_dict(aggregate_variables)
	resources_dict = {}
	for aggregate_variable in aggregate_variables:
		resources_dict[aggregate_variable] = initialize_dict(resource_types)
	return counts, resources_dict


def aggregate_durations(row, aggregate_variable_name, counts, agg_resources_dict, resource_types):
	try:
		aggregate_variable = row[aggregate_variable_name]
		resources_dict = agg_resources_dict[aggregate_variable] #pick the resources_dict by the grade/country of the user
		for resource_type in resource_types:
				value = float(row[resource_type])
				resources_dict[resource_type] += value #add the value of each resource type to the total
		counts[aggregate_variable] += 1
	except KeyError:
		pass #grade or country is not in resources we are trying to capture

def write_agg_durations(aggregate_variable_name, aggregate_variables, counts, agg_resources_dict, resource_types, out_csv_name):
	for aggregate_variable in aggregate_variables:
		resources_dict = agg_resources_dict[aggregate_variable] #pick the resources_dict by the grade/country of the user
		count = counts[aggregate_variable]
		# print aggregate_variable, count

		for resource_type in resources_dict.keys():
			if count != 0:
				resources_dict[resource_type] /= count
			if resources_dict[resource_type] == 0 and resource_type in resource_types:
				resource_types.remove(resource_type) #remove from resource_types list because all resources don't have!
		
	header = [aggregate_variable_name] + resource_types
	resources_dict[aggregate_variable_name] = aggregate_variable
	out_csv = open(out_csv_name, 'wb')
	csv_writer = csv.DictWriter(out_csv, delimiter= ',', fieldnames= header)
	csv_writer.writeheader()

	# remove resources not in list, write to csv
	for aggregate_variable in aggregate_variables: 
		resources_dict = agg_resources_dict[aggregate_variable] 	
		for resource_type in resources_dict.keys():
			if resource_type not in resource_types:
				resources_dict.pop(resource_type)
		resources_dict[aggregate_variable_name] = aggregate_variable 
		csv_writer.writerow(resources_dict)

	out_csv.close()


if __name__ == "__main__":
	# in_csv = open('percent_duration_by_user_grade.csv')
	in_csv = open('total_duration_by_user_grade.csv')
	csv_reader = csv.DictReader(in_csv)
	grades = ['A', 'B', 'C']
	countries = ['US', 'IN', 'CN', 'RU', 'DE', 'PL', 'BR']

	fields = csv_reader.fieldnames
	assert('grade' == fields[0])
	assert('country' == fields[1])
	resource_types = fields[2:] #get the resource type names from the input csv

	grade_counts, grade_resources = initialize_variable_dict(grades, resource_types)
	country_counts, country_resources = initialize_variable_dict(countries, resource_types)

	#sum up the durations for each grade/country and resource_type
	for row in csv_reader:
		aggregate_durations(row, 'grade', grade_counts, grade_resources, resource_types)
		aggregate_durations(row, 'country', country_counts, country_resources, resource_types)

	# write the duration for each grade/country
	# write_agg_durations('grade', grades, grade_counts, grade_resources, resource_types, 'percent_duration_aggregate_by_grade.csv')
	# write_agg_durations('country', countries, country_counts, country_resources, resource_types, 'percent_duration_aggregate_by_country.csv')
	write_agg_durations('grade', grades, grade_counts, grade_resources, resource_types, 'total_duration_aggregate_by_grade.csv')
	write_agg_durations('country', countries, country_counts, country_resources, resource_types, 'total_duration_aggregate_by_country.csv')

	in_csv.close()
