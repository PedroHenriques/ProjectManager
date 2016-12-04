# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#															  #
# Python Project Manager v1.2.0								  #
#															  #
# Copyright 2016, PedroHenriques 							  #
# http://www.pedrojhenriques.com 							  #
# https://github.com/PedroHenriques 						  #
# 															  #
# Free to use under the MIT license.			 			  #
# http://www.opensource.org/licenses/mit-license.php 		  #
# 															  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys

class CLI :
	"""Processes the command line parameters passed to this program when it was called"""

	def __init__(self) :
		# the argument format expected by this program are as follow:
		# 1st arg = the action to be executed (ex: project, file)
		# ... args = dependent on the requested action. See the action's method below for further details

		# instance variables
		# stores the action that should be executed by the program
		self.action = None
		# stores the necessary arguments for the requested action, to be used by the Application class
		self.args = {}

		# check if there are the mandatory #arguments
		# NOTE: there is always an implicit 0th argument with the path to the file being called
		if (len(sys.argv) < 2) :
			# there aren't, so bail out
			print("=> ERROR: The command syntax is invalid.\nFor further information type \"help\".\n")
			return

		# tuple with the valid actions
		valid_action = ("project", "file", "help")

		# check if the action requested is valid
		requested_action = sys.argv[1].lower()
		if (requested_action not in valid_action) :
			# it isn't, so bail out
			print("=> ERROR: The command \"" + requested_action + "\" is not valid.\nFor further information type \"help\".\n")
			return

		# the action is valid, so store it
		self.action = requested_action

		# process any required arguments, for the requested action
		# NOTE: the feedback message is printed by the methods
		if (not getattr(self, "process" + self.action.capitalize(), False)()) :
			# something is wrong with the command line arguments
			self.action = None
			# bail out
			return

	# processes the command line arguments required to create a new project
	def processProject(self) :
		# expected arguments:
		# 2nd arg = the location where the action should be executed
		# 3rd arg = the name of the project to be created
		# 4th arg = the type of project (ex: website, ruby, python)

		# check if all the required arguments are set
		# NOTE: there is always an implicit 0th argument with the path to the file being called
		if (len(sys.argv) < 5) :
			# they aren't, so bail out
			print("=> ERROR: The command syntax is invalid.\nFor further information type \"help " + self.action + "\".\n")
			return(False)

		# make sure the 2nd arg is using backslashes and ends with one
		sys.argv[2] = sys.argv[2].replace("/", "\\")
		if (not sys.argv[2].endswith("\\")) :
			sys.argv[2] += "\\"

		# store the necessary arguments
		# path where the action is to be executed
		self.args["action_path"] = sys.argv[2] + sys.argv[3] + "\\"
		# name of project to be created
		self.args["project_name"] = sys.argv[3]
		# type of project to be created
		self.args["project_type"] = sys.argv[4]

		# all OK
		return(True)

	# processes the command line arguments required to create a new file
	def processFile(self) :
		# expected arguments:
		# 2nd arg = the location where the action should be executed
		# 3rd arg = the name of the file to be created
		# 4th arg = the type of file (ex: php, ruby, python, json)
		# 5th arg = [optional] extra configuration flags (ex: -f)

		# check if all the required arguments are set
		# NOTE: there is always an implicit 0th argument with the path to the file being called
		if (len(sys.argv) < 5) :
			# they aren't, so bail out
			print("=> ERROR: The command syntax is invalid.\nFor further information type \"help " + self.action + "\".\n")
			return(False)

		# make sure the 2nd arg is using backslashes and ends with one
		sys.argv[2] = sys.argv[2].replace("/", "\\")
		if (not sys.argv[2].endswith("\\")) :
			sys.argv[2] += "\\"

		# store the necessary arguments
		# path where the action is to be executed
		self.args["action_path"] = sys.argv[2]
		# name of file to be created
		self.args["file_name"] = sys.argv[3]
		# type of file to be created
		self.args["file_type"] = sys.argv[4]
		# extra configuration flags
		if (len(sys.argv) > 5 and sys.argv[5].startswith("-") and len(sys.argv[5]) > 1) :
			# there are some valid config flags
			self.args["config_flags"] = list(sys.argv[5][1:])
		else :
			# there aren't any valid config flags
			self.args["config_flags"] = []

		# all OK
		return(True)

	# processes the command line arguments required to show the help information
	def processHelp(self) :
		# expected arguments:
		# 2nd arg = [optional] the topic for the information

		# store the necessary arguments
		# desired topic, if 1 was given, or None otherwise
		self.args["topic"] = sys.argv[2] if (len(sys.argv) > 2) else None

		# all OK
		return(True)
