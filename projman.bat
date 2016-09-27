@echo off

REM path to the main.py file of the program
set "file_path=path\to\main.py"

REM if the action is HELP, no processing is required
if {%1} == {help} goto help_action

REM build the desired path for the action to be executed
if {%2} == {.} (
	REM the desired path is the current path
	set "trg_path=%CD%"
) else (
	REM the desired path is relative to the current path
	set "trg_path=%CD%%2"
)

REM build the list of remaining args to be passed to the python program
set "args=%1 %trg_path%"
shift
:loop
shift
if {%1} == {} goto after_loop
set "args=%args% %1"
goto loop
:after_loop

REM call the python program for any action other than HELP
python %file_path% %args%

goto end_file

REM call the python program for the HELP action
:help_action
python %file_path% %*

:end_file
