0.1.19
------

* add Line channel

0.1.18
------

* add Slack and KaKao channel
* add a ``new`` command
* update console messages
* fix: decode error when opening yml file


0.1.17
------

* add a `key` argument to `get_project_data()` and `get_user_data()`


0.1.16
------

* fix: ``ExternalHttpStorageClient.set_user_data`` didn't send data in its payload
* enhancement: use ``prompt-toolkit`` for ``bothub test`` prompt
* add --max-retries option to deploy command


0.1.15
------

* raise test coverage to 80%
* introduce project meta and move some project config properties to it


0.1.14
------

* hotfix: error with os.path.dirname


0.1.13
------

* fix: create .bothub directory, handle that caches.yml file is empty. Thanks to Bokyeong Kwon


0.1.12
------

* add: -l option for ``bothub ls``
* add: --version option
* add: check latest version
* add: check auth token expiration
* tune messages


0.1.11
------

* fix: handle EOF case in ``bothub test``
* fix: consider plain log message case
* fix: inject an event and context object for local NLU test
* update README


0.1.10
------

* keep command history for ``bothub test``
* add a ``logs`` command
* watch deployment progress


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
