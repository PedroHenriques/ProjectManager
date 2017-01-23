# Project Manager

An easily customizable python program that makes it easy to create projects and files with predefined content.

## Instructions

### Setup

#### => Running the program and Batch file:

In order to run the program the file `main.py` must be called from the command line or terminal with the required parameters.  

To facilitate running the program, by being able to call it from any path, the repository comes with a **batch file**.  
This batch file will not only allow the program to be called from any path, as well as allow relative paths to be given as arguments.  

Before being able to use the batch file from any path, it must be placed in a directory that is part of the `PATH` environmental variable (in windows).  
Secondly, in the batch file the line `set "file_path=path\to\main.py"` must be adjusted by changing `path\to\main.py` with the path to the `main.py` file.
Finally, the name given to the batch file will be the name used in the command line to run the program.

#### => Configuring/Customizing the Program

**JSON files:**  

Each action has a JSON file, named after the action, that contains all the data needed for that action's execution.  
The syntax of these files is as follows:
- The data can be organized in as many levels deep as needed
- The data that will be used in the action proper will, in general, treat keys as either file or directory names and their values as either the file or the directory's content.
- Files have `strings` as values. These strings contain the file's content. An empty file should have an empty string as it's value.
- Directories have `objects` as values. These objects contain the files and directories that should go inside this directory. An empty directory should have an empty object as it's value.  

NOTE: The **help** action is an exception to these rules. For further information on the help action consult the related topic below.  

Example:  

```
{
	"python" : {
		".gitignore" : "",
		"main.py" : "print(\"Hello World.\")",
		"classes" : {
			"__init__.py" : "__all__ = [\"Application\"]",
			"Application.py" : "class Application :\n\t\"\"\"This is the application's main class.\"\"\"\n\n\tdef __init__(self) :\n\t\tpass"
		},
		"data" : {}
	}
}
```

In this example, if the program is told to create a new python project (exact syntax further down), inside the project's directory the result would be:
- An empty file named `.gitignore`
- A file named `main.py` with content `print("Hello World.")`
- A directory named `classes`, inside of which is:
	- A file named `__init__.py` with content `__all__ = ["Application"]`
	- A file named `Application.py` with content
	```
	class Application :
		"""This is the application's main class."""

		def __init__(self) :
			pass
	```
- An empty directory named `data`

**Special Keywords:**  

The content of files, created by both the file and the project actions, can have special keywords that will be replaced by dynamic or static data.  

All keywords are in the format `|!keyword{multiplier}[case]!|`.  
- `keyword`: One of the supported keywords. See below for a list of global keywords, as well as, how to add your own.
- `multiplier` (Optional): An integer (whole number) indicating how many times that keyword replacement should be inserted.
- `case` (Optional): A tag indicating a specific case status for the keyword replacement. The supported tags are:
	- `uc`: insert the keyword replacement in UPPERCASE.
	- `lc`: insert the keyword replacement in lowercase.
	- `t`: insert the keyword replacement Capitalized.

The **global keywords** are:  

Keyword | Replace Value | Supported Actions
--- | --- | ---
copyright | copyright text<br>see below for details on how to customize the text | project<br>file
project_name | the new project's name | project<br>file (1)
file_name | the new file's name | project<br>file
file_type | the new file's type | project<br>file
project_type | the new project's type | project
no_www_domain | the new project's name, striped of any starting "www." | project

(1)  When creating a new file, the code will search the file's path for the first directory with a `.git` folder inside it. That directory will be treated as the file's project_name.

Adding **custom keywords**:  

All custom keywords and their replacement strings are defined in the `keywords.json` file.  
Any keywords added to this file will become usable in all the actions.

It is valid to use other keywords in the replacement string. 

This is also where the copyright text is defined and can be customized.  

NOTE: the code expects the keyword to have a string as a value in `keywords.json` and will replace it with an empty string if that is not the case.

### Using the Project Manager

The syntax expected by the program depends on the desired action to be executed.  
The available actions are:  
- project
- file
- help

#### => Project Action:

The **project** action will create a new project directory, populated with any files, plus their content, and directories specified in the `project.json` file.  

The command line syntax for this action is `project location name type` where:
- `location`: path to the directory where the project's folder should be created.<br>If running the program through the batch file a path relative to the working directory can be given, and a `.` can be used to indicate the working directory.<br>If running the program by calling main.py directly, then an absolute path must be given.
- `name`: the name for the project's folder.
- `type`: the type of project to be created.

The `type` of project to be created should match the data available in `project.json` and a `:` should be used to navigate the JSON's tree levels.  

**Example:**  

For a `project.json` file with the following structure:
```
{
	"website" : {
		"php" : {
			...
		},

		"cs" : {
			...
		}
	},

	"python" : {
		...
	}
}
```

And assuming the working directory in the command line is `C:\work`:
- to create a new `php` project named `personal_site` the following command would be used `project . personal_site website:php`.
- to create a new `python` project named `calculator` the following command would be used `project /portfolio calculator python`.

#### => File Action:

The **file** action will create a new file, with the content relevant to its extension, as specified in the `file.json` file.  

The command line syntax for this action is `file location name type [-flags]` where:
- `location`: path to the directory where the file should be created.<br>If running the program through the batch file a path relative to the working directory can be given, and a `.` can be used to indicate the working directory.<br>If running the program by calling main.py directly, then an absolute path must be given.
- `name`: the name for the file (without the extension).
- `type`: the type of file to be created.
- `flags`: optional argument with the desired flags. The supported flags are:<br>`f`: forces the creation of the file by creating any directories in the given path that don't exist.<br>`o` : if a file with the same path already exists, it will be overwritten.

The `type` of file to be created should match the data available in `file.json` and a `:` should be used to navigate the JSON's tree levels.

The code expects `file.json` to have a key `extension` with a string value containing the file's extension and a key `content` with a string value containing the file's content.  

**Example:**  

For a `file.json` file with the following structure:
```
{
	"class" : {
		"php" : {
			"extension" : "php",
			"content" : "..."
		},

		"python" : {
			"extension" : "py",
			"content" : "..."
		}
	},

	"js" : {
		"extension" : "js",
		"content" : "..."
	}
}
```

And assuming the working directory in the command line is `C:\work`:
- to create a new `php class` file named `Player` the following command would be used `file /game Player class:php`.
- to create a new `js` file named `main` the following command would be used `file /site/assets main js`.

#### => Help Action:  

The **help** action will display help information about the program, as specified in the `help.json` file.  

The command line syntax for this action is `help [topic]`.  
If no topic is given, the list of topics will be displayed, otherwise detailed information about the given topic will be displayed.
