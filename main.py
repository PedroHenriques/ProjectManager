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

import traceback, os
from classes import Application

# code that starts the entire application
try :
	# instantiate the application's main class
	app = Application.Application(os.path.dirname(os.path.realpath(__file__)) + "\\data")
except Exception as e :
	traceback.print_exc()
	print("\n")
