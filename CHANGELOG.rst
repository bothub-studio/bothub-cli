0.1.10
------

* keep command history for ``bothub test``


0.1.9
-----

* handle a case no proper project found


0.1.8
-----

* regard value as a str when not valid JSON type
* add location support for ``bothub test``
* use readline for ``bothub test``
* use production server property


0.1.7
-----

* use bothub.yaml and bothub.yml both for config file name
* add a ``nlu`` command


0.1.6
-----

* clone a project code after create the project


0.1.5
-----

* add a ``clone`` command
* refactor cli module to use class, change act of init command to create project even when current directory has bothub.yml but not a valid project


0.1.4
-----

* add a ``bothub`` package dependency
* change an error message
* add subcommand ``ls`` and ``rm`` for ``property`` command
* add a test command


0.1.3
-----

* add long option (-l) to channel ls subcommand
* use terminaltables and apply it to channel and project ls
* add page-access-token option
* fix inifinite loop bug when configure on existing project


0.1.2
-----

* fix README bug


0.1.1
-----

* Add version number to module
* Add description to commands
* Add ``app-id``, ``app-secret`` options to ``channel add`` for FB messenger channel
