# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#															  #
# Python Project Manager v1.3.0								  #
#															  #
# Copyright 2016, PedroHenriques 							  #
# http://www.pedrojhenriques.com 							  #
# https://github.com/PedroHenriques 						  #
# 															  #
# Free to use under the MIT license.			 			  #
# http://www.opensource.org/licenses/mit-license.php 		  #
# 															  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os, json, re
from classes import CLI

class Application :
	"""This is the application's main class."""

	def __init__(self, json_path) :
		# instance variables
		# path to the directory with the JSON files
		self.json_path = json_path.replace("/", "\\")
		# contains the keywords to be replaced in the files content and the replacement strings
		self.keywords = {}
		# stores the decoded content of the action's JSON file
		self.json_data = {}
		# instantiate the CLI class to process what should be done by the program
		self.cli_obj = CLI.CLI()

		# check if the command provided is valid
		if (self.cli_obj.action == None) :
			# it isn't
			# NOTE: the feedback message is printed by the CLI class
			return

		# make sure json_path ends with a backslash
		if (not self.json_path.endswith("\\")) :
			self.json_path += "\\"

		# make sure the action's JSON file exists
		action_json_path = self.json_path + self.cli_obj.action + ".json"
		if (not os.path.isfile(action_json_path)) :
			# it doesn't, so bail out
			print("=> ERROR: Couldn't find the \"" + self.cli_obj.action + ".json\" file.")
			return()

		# instantiate the JSON decoder
		self.json_decoder = json.JSONDecoder()

		# grab the parsed content of this action's JSON file
		self.json_data = self.parseJSON(action_json_path)

		# grab the parsed content of keywords.json file, if it exists
		keywords_json_path = self.json_path + "keywords.json"
		if (os.path.isfile(keywords_json_path)) :
			self.keywords = self.parseJSON(keywords_json_path)

		# call the method that will execute the requested action
		# NOTE: the feedback message is printed by the methods
		if (not getattr(self, "execute" + self.cli_obj.action.capitalize(), False)()) :
			# something went wrong while executing the action, so bail out
			return

	# opens and decodes the contents of the provided JSON file
	# NOTE: checking if the file exists should be done by the caller method
	def parseJSON(self, file_path) :
		# grab the content of the json file
		file_object = open(file_path, "r", encoding = "utf-8")
		json_string = file_object.read()
		file_object.close()

		# decode json_string and return it
		return(self.json_decoder.decode(json_string))

	# creates a new project
	# returns True if successful, False otherwise
	def executeProject(self) :
		# create the necessary local variables
		project_name = self.cli_obj.args["project_name"]
		project_type = self.cli_obj.args["project_type"]
		project_path = self.cli_obj.args["action_path"]

		# get the information relevant for the desired project_type
		if (not self.updateJsonData(project_type)) :
			# the project_type isn't defined, so bail out
			print("=> ERROR: The project type \"" + project_type + "\" isn't defined in \"" + self.cli_obj.action + ".json\".\n")
			return(False)

		# this string will be inserted into any file's content where |!project_name!| is present
		self.keywords["project_name"] = project_name.title()
		# this string will be inserted into any file's content where |!project_type!| is present
		self.keywords["project_type"] = project_type
		# this string will be inserted into any file's content where |!no_www_domain!| is present
		self.keywords["no_www_domain"] = project_name[4:] if (project_name.startswith("www.")) else project_name

		# create the project's directory
		try :
			os.makedirs(project_path)
		except OSError as e :
			# the project's directory already exists
			print("=> ERROR: The project's directory couldn't be created.")
			return(False)

		# create the structure
		if (not self.createStructure(self.json_data, project_path)) :
			# something went wrong
			# remove any of the structure created
			self.deleteDir(project_path)

			# bail out
			# NOTE: any error messages should be printed by createStructure()
			return(False)

		# at this point everything went OK
		print("=> Success: Project " + project_name + " created!")
		return(True)

	# creates a new file
	# returns True if successful, False otherwise
	def executeFile(self) :
		# create the necessary local variables
		file_name = self.cli_obj.args["file_name"]
		file_type = self.cli_obj.args["file_type"]
		file_path = self.cli_obj.args["action_path"]
		config_flags = self.cli_obj.args["config_flags"]

		# get the information relevant for the desired file_type
		if (not self.updateJsonData(file_type)) :
			# the file_type isn't defined, so bail out
			print("=> ERROR: The file type \"" + file_type + "\" isn't defined in \"" + self.cli_obj.action + ".json\".\n")
			return(False)

		# extract the file's extension from self.json_data
		file_extension = self.json_data["extension"]
		# update self.json_data to be the file's content
		self.json_data = self.json_data["content"]

		# at this point self.json_data should be a string with the content for the requested file_type
		if (not isinstance(self.json_data, str)) :
			# self.json_data is not a string, so bail out
			print("=> ERROR: The file type \"" + file_type + "\" isn't valid for \"" + self.cli_obj.action + ".json\".")
			return(False)

		# process the flags
		if ("f" in config_flags) :
			# if the config flag "f" was given, create all the directories in the file's path that don't exist
			# create all the directories as needed (ignoring the exceptions when a directory already exists)
			# if any directory can't be created an error message will be given later when the file fails to be created
			os.makedirs(file_path, exist_ok = True)
		elif ("o" not in config_flags) :
			# if the config flag "o" was NOT given, don't create the file if it already exists
			# check if the file already exists
			if (os.path.exists(file_path + "\\" + file_name + "." + file_extension)) :
				# it does, so bail out
				print("=> ERROR: The file already exists. Use the flag \"o\" if you want the existing file to be overwritten.")
				return(False)

		# this string will be inserted into any file's content where |!project_name!| is present
		# since the project name wasn't provided in the cmd find it based on the file's destination
		self.keywords["project_name"] = self.findProjectName(file_path)
		# this string will be inserted into any file's content where |!file_name!| is present
		self.keywords["file_name"] = file_name
		# this string will be inserted into any file's content where |!file_type!| is present
		self.keywords["file_type"] = file_type

		# create the structure
		if (not self.createStructure({file_name + "." + file_extension : self.json_data}, file_path)) :
			# something went wrong, bail out
			# NOTE: any error messages should be printed by createStructure()
			# delete the file
			try :
				os.remove(file_path + file_name)
			except OSError as e :
				pass

			return(False)

		# at this point everything went OK
		print("=> Success: File " + file_name + " created!")
		return(True)

	# show help information
	# returns True if successful, False otherwise
	def executeHelp(self) :
		# create the necessary local variables
		topic = self.cli_obj.args["topic"]

		# process the requested topic
		help_string = ""
		if (topic == None) :
			# no topic was provided
			# show the list of topics
			help_string += "=> To obtain information about a specific topic type \"help topic_name\", where topic_name is one of the following:"

			# loop through the topics that have help information
			for key in self.json_data :
				help_string += "\n\t- " + key
		else:
			# a topic was provided
			# split the topic into its parts
			topic_parts = topic.split(":")

			# check if a sub topic was provided
			sub_topic = True
			if (len(topic_parts) == 1) :
				# it wasn't
				sub_topic = False

				# ask for the base information about this topic
				topic += ":base"

				# update the topic parts
				topic_parts = topic.split(":")

			# get the information relevant for the desired topic
			if (not self.updateJsonData(topic)) :
				# the file_type isn't defined, so bail out
				print("=> ERROR: The topic \"" + topic + "\" isn't defined in \"" + self.cli_obj.action + ".json\".\n")
				return(False)

			# at this point self.json_data should be a string with the help text for the requested topic
			if (not isinstance(self.json_data, str)) :
				# self.json_data is not a string, so bail out
				print("=> ERROR: The topic \"" + topic + "\" isn't valid in \"" + self.cli_obj.action + ".json\".\n")
				return(False)

			# store the help string
			help_string = self.json_data

			# if a subtopic was provided, add the extra information
			if (sub_topic) :
				if (topic_parts[1] == "type") :
					# get the relevant JSON file's content
					sub_topic_json_data = self.parseJSON(self.json_path + topic_parts[0] + ".json")

					# check if the topic is "project"
					if (topic_parts[0] == "project") :
						# it is, so only loop through the 1st tier of the JSON file
						# loop through the JSON's content
						for key in sub_topic_json_data :
							help_string += "\n\t- " + key
					else :
						# it isn't, so loop through all the tiers of the JSON file
						# loop through the JSON's content
						for key in sub_topic_json_data :
							help_string += "\n\t- " + self.buildTypesString(key, sub_topic_json_data[key])

		# print the help text
		print(help_string)

		# at this point everything went OK
		return(True)

	# builds and returns a string with all the type supported by the various actions
	# NOTE: called recursively
	def buildTypesString(self, parent_str, data) :
		res = ""

		# loop through the data
		for key in data :
			# check if key's value is a string
			if (isinstance(data[key], str)) :
				# it is, so this is an end tier which is to be ignored
				continue

			# this isn't an end tier
			# update the type string with this tier's sub-tiers
			res += self.buildTypesString(parent_str + ":" + key, data[key]) + "  "

		# check if this tier had any valid sub-tiers
		if (len(res) == 0) :
			# it didn't, so the type is the tier itself
			res = parent_str

		return(res.strip())

	# searches the selected JSON file for the needed information
	# the changes will be made to self.json_data
	# return True if successful or False otherwise
	def updateJsonData(self, keys_str) :
		# split the string with the keys into a list
		keys = keys_str.split(":")

		# loop through the keys
		for key in keys :
			# use the key in lowercase
			key = key.lower()

			# check if this key exists in the JSON file
			if (key not in self.json_data) :
				# the key isn't defined, so bail out
				return(False)

			# the key exists, so update self.json_data
			self.json_data = self.json_data[key]

		# at this point everything went OK
		return(True)

	# builds the copyright text, based on the file's extension
	def buildCopyrightString(self, file_extension) :
		# check if there is information for the requested file_extension
		if (file_extension not in self.keywords["copyright"]["replaces"]) :
			# there isn't, so bail out
			return("")

		# build the dictionary with relevant keywords and replacement strings
		# start by add all the keywords
		replacements = self.keywords.copy()

		# remove the copyright entries
		del replacements["copyright"]

		# add the copyright replaces relevant for this file extension
		replacements.update(self.keywords["copyright"]["replaces"][file_extension])

		# add the general replaces, if any
		if ("general" in self.keywords["copyright"]["replaces"]) :
			replacements.update(self.keywords["copyright"]["replaces"]["general"])

		# replace the placeholders with this file's extension copyright information
		# and return the finished copyright text
		return(self.replaceKeyWords(replacements, self.keywords["copyright"]["text"]))

	# loops through the structure and creates all the files and folders
	# with their respective content
	# return True if successful or False otherwise
	def createStructure(self, structure, path) :
		# loop each item and process them
		for key in structure :
			# determine if this entry is a file or a directory
			if (isinstance(structure[key], str)) :
				# this entry is a file

				# grab the content to be inserted in this file
				file_content = structure[key]

				# build the dictionary with replacement keywords
				replacements = self.keywords.copy()

				# determine this file's extension
				aux_pos = key.rfind(".")
				if (aux_pos == -1) :
					file_extension = ""
				else :
					file_extension = key[aux_pos + 1:]

				# add this file's name and type to the replacements
				replacements["file_name"] = key[:aux_pos]
				replacements["file_type"] = file_extension

				# check if this file requires the copyright text to be inserted
				if ("|!copyright!|" in file_content) :
					# it does
					# add the copyright replacement information
					replacements["copyright"] = self.buildCopyrightString(file_extension)

				# replace the keywords with their respective new strings
				file_content = self.replaceKeyWords(replacements, file_content)

				# create and open the file in write mode
				try :
					file_object = open(path + key, "w", encoding = "utf-8")
					file_object.write(file_content)
					file_object.close()
				except OSError as e :
					# the file couldn't be created
					print("=> ERROR: The file \"" + key + "\" couldn't be created.\nMake sure all directories in the path provided exist.")
					return(False)
			elif (isinstance(structure[key], dict)) :
				# this entry is a directory
				try :
					# create the new path with this folder
					new_path = path + "\\" + key + "\\"

					# create the folder
					os.mkdir(new_path)

					# check if this folder has folders and/or files inside it
					if (len(structure[key]) > 0) :
						# it has, so call this method recursively
						if (not self.createStructure(structure[key], new_path)) :
							# something couldn't be created
							print("=> ERROR: The directory \"" + key + "\" already exists.")
							return(False)
				except OSError as e :
					# the directory couldn't be created
					print("=> ERROR: The directory \"" + key + "\" already exists.")
					return(False)
			else :
				# the data type of this entry is not valid
				# ignore, but give message
				print("=> Warning: The value for the key \"" + key + "\" is not valid.")

		# at this point everything went ok
		return(True)

	# recursive method that will delete a directory and all its contents
	# returns True if successful, False if not
	def deleteDir(self, path) :
		# if the path is NOT a folder, return False
		if (not os.path.isdir(path)) :
			return(False)

		# loop through each item in this directory
		for item in os.listdir(path) :
			# build the items full path
			item_path = path + "\\" + item

			# if this item is a file, delete it
			if (os.path.isfile(item_path)) :
				os.remove(item_path)
			else :
				# it's a directory, so call this method with the directory's path
				if (not self.deleteDir(item_path)) :
					# the directory could not be deleted
					return(False)

		# now that we have cleared this directory of items, delete it
		try :
			os.rmdir(path)
		except OSError as e :
			# the directory could not be deleted
			return(False)

		# at this point everything went ok
		return(True)

	# searches the string for |!keyword!| and replaces them
	# NOTE: any keywords found in string not present in replacements will be replaced by an empty string
	def replaceKeyWords(self, replacements, string) :
		# the pattern to identify the placeholders
		re_pattern = "\|!([^{!\[\]]+)(\{\d+\})?(\[[^{!\[\]]+\])?!\|"

		# the map between case tag in the regex and the String class function to use
		str_func = {"lc" : "lower", "uc" : "upper", "t" : "title"}

		# loop while there are keywords in the string
		re_matches = re.search(re_pattern, string)
		while (re_matches != None) :
			# grab the re_matches groups
			match_groups = re_matches.groups("")
			match_count = len(match_groups)

			# check if the keyword found is present in replacements and is a string
			if (match_groups[0] in replacements and isinstance(replacements[match_groups[0]], str)) :
				# it is
				# build the replacement string
				new_string = replacements[match_groups[0]]
			else :
				# it isn't
				# replace the keyword with an empty string
				new_string = ""

			# check if there is any other information provided
			if (len(new_string) > 0 and match_count > 1) :
				# there is
				# loop through the remaining matches
				i = 1
				while (i < match_count):
					# check if this match is a multiplier
					if (match_groups[i].startswith("{") and match_groups[i].endswith("}")) :
						# it is
						# update the replacement string
						new_string *= int(match_groups[i][1:-1])
					# check if this match is a case enforcer
					elif (match_groups[i].startswith("[") and match_groups[i].endswith("]")) :
						# it is
						# check if this case enforcer is valid
						case_enforcer = match_groups[i][1:-1].lower()
						if (case_enforcer in str_func) :
							# it is
							# update the replacement string
							new_string = getattr(new_string, str_func[case_enforcer], new_string)()

					i += 1

			# replace the keyword with the new_string
			string = string.replace("|!" + "".join(match_groups) + "!|", new_string)

			# check the pattern again
			re_matches = re.search(re_pattern, string)

		# return the final string
		return(string)

	# searches all the directories in the path provided for the project folder
	# the project folder is the 1st folder found with a ".git" directory
	# if none can be found, then an empty string will be returned
	def findProjectName(self, destination_path) :
		result = ""

		# loop through the path provided untill a ".git" folder is found or the drive folder is reached
		while (re.search("^[a-zA-Z]:\\\\$", destination_path) == None) :
			# check if this directory has a ".git folder"
			if (".git" in os.listdir(destination_path)) :
				# it does
				result = re.search("^.+\\\\([^\\\\]+)\\\\?$", destination_path).group(1)
				break

			# move to the parent directory
			destination_path = os.path.dirname(destination_path)

		# cosmetic changes to the result
		result = result.title()

		return(result)
