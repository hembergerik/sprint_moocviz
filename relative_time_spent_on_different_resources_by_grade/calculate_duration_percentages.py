# Created on Oct 3rd, 2013
# Refactored on Oct 11, 2013
# @author: Sherwin Wu for ALFA, MIT lab: sherwu@mit.edu
# @author: Colin Taylor, colin_t@mit.edu
# =============================
# IMPORTANT!!!
# This script will output a file called 'duration_by_user_grade.csv'
# =============================

import MySQLdb as mdb
import json
import csv

def initialize_dict(resource_types):
	temp_dict = {}
	for resource_type in resource_types:
		temp_dict[resource_type] = 0
	return temp_dict

def write_row_to_csv(resource_types, resource_to_time, total_time, old_final_grade, old_country, percent_csv_writer, total_csv_writer):
	resource_to_time['grade'] = grades_dict[float(old_final_grade)]
	resource_to_time['country'] = old_country

	total_csv_writer.writerow(resource_to_time)

	for resource_type in resource_types:
		resource_to_time[resource_type] /= float(total_time)

	percent_csv_writer.writerow(resource_to_time)

def initialize_state(user_id, user_country, final_grade, resource_types):
	current_user_id = user_id
	old_country = user_country
	old_final_grade = final_grade
	total_time = 0
	resource_to_time = initialize_dict(resource_types)
	return (current_user_id, old_country, old_final_grade, total_time, resource_to_time)


if __name__ == "__main__":
	connection = mdb.connect('127.0.0.1', '', '', 'moocdb', port=3306, charset='utf8')

	cursor = connection.cursor()
	cursor.execute("""
		SELECT observed_events.user_id AS user_id,
			SUM(observed_events.observed_event_duration) AS duration,
			users.user_final_grade AS grade,
			users.user_country AS country,
			resource_types.resource_type_content AS resource_type
		FROM moocdb.observed_events AS observed_events,
			moocdb.users AS users, moocdb.resources_urls AS resources_urls,
			moocdb.resources AS resources, moocdb.resource_types AS resource_types
		WHERE (users.user_final_grade=1 OR users.user_final_grade=0.75 OR users.user_final_grade=0.5)
			AND users.user_id = observed_events.user_id
			AND resources_urls.url_id = observed_events.url_id
			AND resources.resource_id = resources_urls.resource_id
			AND resource_types.resource_type_id = resources.resource_type_id
		GROUP BY user_id, resource_type;
	""")
	

	percent_out_csv = open('percent_duration_by_user_grade.csv', 'wb')
	total_out_csv = open('total_duration_by_user_grade.csv', 'wb')
	resource_types = ['lecture', 'tutorial', 'informational', 'problem', \
		'exam', 'wiki', 'forum', 'profile', 'index', 'book', 'survey', 'home', \
		'other']

	header = ['grade', 'country'] + resource_types
	percent_csv_writer = csv.DictWriter(percent_out_csv, delimiter= ',', fieldnames= header)
	percent_csv_writer.writeheader()
	total_csv_writer = csv.DictWriter(total_out_csv, delimiter= ',', fieldnames= header)
	total_csv_writer.writeheader()


	current_user_id = None
	grades_dict = {1: 'A', 0.75: 'B', 0.5: 'C', None: 'no grade'}

	for i in range(cursor.rowcount):
		(user_id,total_duration,final_grade,user_country,resource_name) = cursor.fetchone()
		user_id = int(user_id)
		total_duration = int(total_duration)		

		if current_user_id == None:
			current_user_id, old_country, old_final_grade, total_time, resource_to_time = \
				initialize_state(user_id, user_country, final_grade, resource_types)

		if user_id != current_user_id: #found a new user- write the old row to csv
			write_row_to_csv(resource_types, resource_to_time, total_time, old_final_grade, old_country, percent_csv_writer, total_csv_writer)

			#create the new dictionary for new user
			current_user_id, old_country, old_final_grade, total_time, resource_to_time = \
				initialize_state(user_id, user_country, final_grade, resource_types)

		if resource_name in resource_to_time:
			resource_to_time[resource_name] = total_duration
		total_time += total_duration

		if i == cursor.rowcount - 1: #last user- write old row to csv
			write_row_to_csv(resource_types, resource_to_time, total_time, old_final_grade, old_country, percent_csv_writer, total_csv_writer)		
		
	percent_out_csv.close()
	total_out_csv.close()
	connection.close()
