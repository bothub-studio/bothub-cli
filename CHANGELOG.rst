0.1.6
-----

* use bothub.yaml and bothub.yml both for config file name
* add a ``nlu`` command


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
