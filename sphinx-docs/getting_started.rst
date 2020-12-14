***************
Getting Started
***************

========
Overview
========

Slivka is a free software which provides easy and convenient means
for creating web services on your local computer, server or cluster.
It is written in Python and is available as a source code or from anaconda.

The core of the system is the scheduler which manages jobs execution,
parses command line arguments and delegates tasks to runners that
start new processes. It uses mongo database to store and exchange data
with the REST server which communicates with client applications --
takes their requests and provides information about running jobs.

.. figure:: overview.svg

  Diagram of interactions between slivka system components.
  The REST server pushes new requests to the database where
  the scheduler picks them from and dispatches to the correct
  runner. The instructions how to create web services and run
  command line programs are taken from the config files.

---------
Scheduler
---------

Scheduler sits in the middle of the job processing and controls other
components.
When the scheduler is started, it creates runners (more on that later)
for each web service specified in the configuration files.
Then it enters its main operation mode in which it constantly monitors
the database and running jobs. Whenever a new request appears in the
database, the scheduler converts job parameters such as files, flags
and other input provided by the user into command line arguments.
They are then passed to the runner for execution and the scheduler
starts watching the job execution and writes its current status
back to the database.

-----------
REST server
-----------

REST server complements the scheduler providing a web interface
which users and client applications can use to submit new jobs
to the system.
On startup, it creates a form for each service specified in the
configuration file. The form contains the list of parameters
which the user is expected to provide to start the job.
Each parameter comes with label, description, type and
optional constraints to inform the user what values are allowed.
When the job request with input parameters is received from the
client, the values are validated and, if correct, saved to
the database for the scheduler to pick them up.

-------
Runners
-------

When talking about the scheduler, we mentioned that it passes jobs to 
the runners for execution. Runners are internal parts of the slivka system
(custom Runners can be created though) which provide an interface
between the scheduler and the software available on the operating system.
Each runner provides code that can start command line programs
and monitor their execution state. If you are an advanced user,
this allows you to write plugins that run your programs in new ways.

------------
Config files
------------

Configuration files live outside of the slivka module and provide
system settings and service information. As a system
administrator, you are responsible for creating and maintaining
those configuration files, so the rest of this tutorial will be mostly
dedicated to them.

============
Installation
============

Slivka is provided as a source code and an Anaconda package. Using
conda is strongly recommended, but it can also be installed with pip
or setuptools once the source code is obtained. Make sure that the
programs you intend to run are accessible from where the slivka is
installed (machine or VM). They don't have to be in the same virtual
python/conda environment though.

Installation requires Python 3.5+ (version 3.7 recommended).
Additional requirements that will be downloaded and installed 
automatically, include:

- attrs (>=19)
- click (>=7.0)
- Flask (>=1.0)
- frozendict (>=1.2)
- gunicorn (>=19.9) (optional)
- jsonschema (>=2.5.1)
- MarkupSafe (>=1.0)
- pymongo (>=3.7)
- PyYAML (>=3.11)
- pyzmq (>=17.0)
- simplejson (>=3.16)
- uwsgi (>=2.0) (optional)
- Werkzeug (>=0.15)


---------------------
Installing with conda
---------------------

Conda installation is recommended due to its simplicity. If you want
to use a dedicated virtual environment create it and install slivka with:

.. code:: 

  conda create -n <env> python=3.7
  conda install -n <env> -c mmwarowny -c conda-forge slivka
  conda activate <env>

substituting environemnt name (e.g. slivka) for ``<env>``.
More information can be found in `conda documentation`_.

.. _`conda documentation`: https://conda.io/en/latest/

-----------------------
Installing from sources
-----------------------

If you are a developer wanting to tweak slivka code to own needs
or you simply don't want to depend on conda then installation from
sources is the way to go.

Either clone the git repository ``https://github.com/bartongroup/slivka.git``
or download and extract the zip archive here_. We suggest using
a more up-to-date development branch until the first stable version
is released.

.. _here: https://github.com/bartongroup/slivka/archive/dev.zip

Navigate to the package directory (the one containing *setup.py*) and run ::

  python setup.py install

You can also use a shortcut command which automatically installs slivka
from the git repository with pip ::

  pip install git+git://github.com/bartongroup/slivka.git@dev

--------------
Mongo database
--------------

Slivka makes use of `mongo database`_ to store data and exchange
messages between its components which is crucial for its operation.
If you do not have mongodb running on your system you can install it
locally in your conda environment or ask your system administrator
to install it system-wide.

.. _`mongo database`: https://www.mongodb.com


==============
Running slivka
==============

--------------------
Creating new project
--------------------

A slivka project is a single instance of slivka with its own settings
and collection of services. You can create as many instances as you want
each running in a separate directory.

During installation, a ``slivka`` executable was created and added to
your path. It can be used to initialize new projects and run slivka.

Let us start with initializing an empty project. To do this, run ::

   slivka init <name>

replacing ``<name>`` with the name of the directory where the configuration 
files will be stored in.
Use ``.`` if you wish to set-up the project in the current directory.

.. note::

  If the slivka executable cannot be accessed directly it can also be
  run as a python module ::

     python -m slivka [args...]

The newly created directory will contain default setting files and 
an example service. In the following sections we will walk through the 
process of creating and configuring new services.

-----------
Starting up
-----------

At this point you are ready to launch a newly created slivka project.
Navigate to the project directory and start three processes ::

  slivka start server &
  slivka start scheduler &
  slivka start local-queue &

It launches a HTTP server, a scheduler and a simple worker queue locally
(``&`` runs them in background, use ``fg`` command to bring them back).

.. note::

  If your mongo database uses listening port other than default
  or any of the ports used by slivka is already in use you can
  change it in the *settings.yaml* file.

--------------
Submitting job
--------------

Now, you can send a GET request or navigate with your web browser to
`<http://127.0.0.1:8000/api/services>`_ to see the list of currently
available services, or one "Example Service" to be specific.

Moving on to */api/services/example* will show you the details of 
the service along with the list of form fields a.k.a. input parameters
of that service. Don't worry if the details doesn't make much sense
yet. For now, notice one field named *msg* which we are going to use.

.. code:: json

  {
    "type": "text",
    "name": "msg",
    "label": "Message",
    "description": "Message printed to the output file",
    "required": true,
    "multiple": false,
    "default": null,
    "minLength": 3,
    "maxLength": 15
  }

This tells us that one of the parameters the example service accepts
is named "msg", it is a required parameter and its length should be
between 3 and 15 characters. In order to submit a new job, send a POST
request to that endpoint providing a value for the *msg* parameter. 
Using curl:

.. code:: sh

  curl -d"msg=hello world" http://localhost:8000/api/services/example

Congratulations, you've just submitted the first job to your slivka
instance. You should have received the id of the newly created job and
slivka should have started working on it.

====================
Configuring services
====================

Until now, we've only seen and submitted a job to the existing example
service. In this section we will take a closer look into the configuration
file of the example service and learn how to create our own services.

Navigate to the *services* folder in your slivka project directory.
It contains a single *example.service.yaml* file. 

=================
Project Structure
=================

First, let us take a look at the overall file structure of the newly 
created project. The project root directory contains three files and 
a *services* directory by default.

:manage.py:
  Legacy executable script which loads all configuration files and starts
  slivka processes. Replaced by *slivka* executable.
:settings.yaml:
  Settings file containing project-wide constants.
  Refer to `settings file`_ section for more information about available
  parameters.
:wsgi.py:
  Module containing a wsgi-compatible application as specified in 
  `PEP-3333`_ used by the dedicated wsgi middleware.
:services:
  Directory containing configuration files for services.
  Refer to `service definition`_ section for more
  information on creating web services.

.. _`PEP-3333`: https://www.python.org/dev/peps/pep-3333/

All the configuration files are using `YAML <https://yaml.org/>`_ syntax 
and can be edited with any text editor.
If you are not familiar with YAML structure you can use JSON instead since
any JSON document is a valid YAML document as well.

It's not advisable to edit *manage.py* and *wsgi.py* scripts unless
you are an advanced user and you know what you are doing.

-------------
Settings file
-------------

``settings.yaml`` is a yaml file containing constant values used by the
application. All parameters are case sensitive and their names should be
written in capital letters.

When slivka is started, a ``SLIVKA_HOME`` environment variable pointing
to the directory containing the settings file is set if not already set.
This variable is used whenever relative paths need to be resolved.

The following parameters should be present in the settings file:

:``VERSION``:
  Version of the settings syntax used. Should be set to ``"1.1"`` for
  the current version.

:``UPLOADS_DIR``:
  Directory where the user uploaded files will be saved to.
  It can be either an absolute path or a path relative to the ``SLIVKA_HOME``
  directory.

  Default: ``./media/uploads``

  .. note::
    If slivka is served behind a reverse proxy, it's recommended to configure
    the proxy server to send files directly from this directory to reduce
    the load put on the python application.

:``JOBS_DIR``:
  Directory where job working directories are created and output files 
  are stored.  Can be either an absolute path or path relative to the
  ``SLIVKA_HOME`` directory.

  Default: ``./media/jobs``

  .. note::
    If slivka is served behind a reverse proxy, it's recommended to configure
    the proxy server to send files directly from this directory to reduce
    the load put on the python application.

:``LOG_DIR``:
  Log files directory location. Can be either an absolute path or a 
  path relative to the ``SLIVKA_HOME`` directory.

  Default: ``./logs``

:``SERVICES``:
  Path to the directory containing service definition files.
  Can be either an absolute path or a path relative to the ``SLIVKA_HOME``
  directory.

  Default: ``./services``

:``UPLOADS_URL_PATH``:
  The URL path where the uploaded files will be available from.
  This setting enables you to set the path so the files can be served 
  by a proxy server e.g. Apache or Nginx. Serving media files through
  the python application is not recommended due to the limited number 
  of simultaneous connections.

  Default: ``/media/uploads``

:``JOBS_URL_PATH``:
  The URL path where the tasks output files will be available from.
  This setting enables you to set the path so the files can be served
  by a proxy server e.g. Apache or Nginx. Serving media files through
  the python application is not recommended due to the limited number
  of simultaneous connections.

  Default: ``/media/jobs``

:``ACCEPTED_MEDIA_TYPES``:
  The list of media types that will be accepted by the server.
  Files having media types not specified in this list could not be 
  uploaded to the server.

  Example:

  .. code-block:: yaml

    ACCEPTED_MEDIA_TYPES:
      - text/plain
      - application/json

:``SECRET_KEY``:
  Randomly generated key used for authentication. Not used currently 
  and might be removed in the future.

:``SERVER_HOST``:
  The hostname which the server will be available at. Setting it to 0.0.0.0
  makes the application accept any incoming connection.
  If the slivka server is running behind a proxy, it's recommended to accept
  the connections from the proxy server only e.g. 127.0.0.1.

:``SERVER_PORT``:
  Port used for listening to the HTTP requests. Note that using
  port number lower than 1024 may not be allowed on your system.

:``URL_PREFIX``:
  *(optional)* Prefix prepended to all API urls. Should be used in
  case you wish Slivka to be asseccible at the location other than 
  the root path. e.g. ``/slivka``.

:``SLIVKA_QUEUE_ADDR``:
  Binding socket of the slivka queue. Can be either tcp or ipc socket.
  **It's highly recommended to use localhost or named pipes.**
  **Accepting external connections is a security issue.**

  Example:

  .. code-block:: yaml

    SLIVKA_QUEUE_ADDR: 127.0.0.1:3397

  .. code-block:: yaml

    SLIVKA_QUEUE_ADDR: /home/slivka/local-queue.sock

:``MONGODB``:
  The connection address to the mongo database.
  It should be a full `mongodb URI`_ e.g. ``mongodb://mongodb.example.com:27017/database``
  or a simple hostname e.g. ``127.0.0.1:27017/database``.
  Alternatively, a mapping containing keys: ``host`` or ``socket`` and ``database``
  and optionally ``username`` and ``password`` can be used instead.

  .. code-block:: yaml

    MONGODB: mongodb://user:pass@127.0.0.1:27017/myDB

    MONGODB:
      username: user
      password: pass
      host: 127.0.0.1:27017
      database: myDB

.. _mongodb URI: https://docs.mongodb.com/manual/reference/connection-string/

------------------
Service Definition
------------------

Service definition files are located in the directory specified in the settings
(*services/* by default).
Each service definition is a separate file named *<name>.service.yaml*
(``[\w_-]*\.service\.ya?ml`` for those familiar with regex)
where service name should be substituted for *<name>* placeholder.
The name should contain alphanumeric characters, dashes and underscores only
and will be used as an unique identifier for the service.
Using lowercase letters is recommended but not required.
You can add as many services as you need as long as each name is unique.

Service Metadata
================

The first thing that need to be included in the service definition file is
its metadata.

The first key in the service file should be the service ``label``.
The label will be presented to the users and should be short and descriptive.

The second key are the service ``classifiers``. It should be a list of tags that
allow to categorise the service based on inputs/outputs or performed operation.
There are no rules for classifiers but ideally they should be both human and
machine readable.

Example:

.. code-block:: yaml

  label: MyService
  classifiers:
    - Purpose=Example
    - Type=Tutorial

Form Definition
===============

Slivka forms serve the same role as web forms -- they are collections of
fields representing input parameters which are populated and submitted by
the users. They also define which parameters are exposed through the web API
and modifiable by the users. Values provided in the form are further 
used to create command line arguments.

Each form field has a unique name (which will be used as a parameter key
when the job is submitted), a short label, a description and allowed
value contraints.

The form is created using ``form`` key containing the mapping of the
field name to their corresponding `field object`_.
As with services, field name should contain alphanumeric characters,
dashes and underscores only (preferably lowercase) and serve as unique
field identifiers.

Field Object
------------
Each element of the form definition consists of the key-value pair
where key is the field name and the value is the field object
having the following properties:

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - label
    - string
    - **Required.** A human readable field name.
  * - description
    - string
    - Detailed information about the field / Help text
  * - value
    - `Value Object`_
    - **Required.** Accepted value metadata: type and constraints


Example of the form accepting two fields: *input* and *filename* is shown below:

.. code-block:: yaml

  input:
    label: Input file
    description: JSON, YAML or XML file containing input data.
    value:
      type: file
  filename:
    label: Filename
    value:
      type: text


Value object
------------

The value object contains the metadata defining the accepted value type and
constraints. Those parameters are used to validate the user-provided input.
The available constraints differ dependingon the field type; however,
properties: ``type``, ``required``, ``default`` and ``multiple`` are
available for all field types.

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - type
    - string
    - **Required.** Type of the field, must be either one of the built-in
      types: int, decimal, text, flag, choice or file; or the path to the
      custom field class.
  * - required
    - boolean
    - Whether the field value must be provided by the user. Default: yes
  * - default
    - any
    - Default value used if no value is provided by the user. The default
      value must also meet all value constraints.
  * - multiple
    - boolean
    - Whether the field accepts multiple values. Default: no

Note that specifying the default value automatically makes the field not
required since the default value is used when the field is left empty.

All other parameter listed below are optional and are specific to
their respective field types.

int type
''''''''

===== ========= =========================
 Key   Type      Description
===== ========= =========================
min   integer   Minimum value, unbound if not provided.
max   integer   Maximum value, unbound if not provided.
===== ========= =========================

Example:

.. code-block:: yaml

  type: int
  required: true
  min: 0
  max: 10
  default: 5


decimal type
''''''''''''

============== ======= =======================================
 Key            Type    Description
============== ======= =======================================
min            float   Minimum value, unbound if not provided.
max            float   Maximum value, unbound if not provided.
min-exclusive  boolean Whether the minimum should be excluded.
max-exclusive  boolean Whether the maximum should be excluded.
============== ======= =======================================

Example:

.. code-block:: yaml

  type: decimal
  min: -4.0
  min-exclusive: false
  max: 4.5
  max-exlusive: true
  default: 0

text type
'''''''''

=========== ======== ===============================
 Key         Type     Description
=========== ======== ===============================
min-length  integer  The minimum length of the text.
max-length  integer  The maximum length of the text.
=========== ======== ===============================

Example:

.. code-block:: yaml

  type: text
  min-length: 1
  max-length: 8

flag type
'''''''''

===== ========= =========================
 Key  Type      Description
===== ========= =========================
 *(no additional properties)*
=========================================

Example:

.. code-block:: yaml

  type: flag
  default: false

choice type
'''''''''''

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - choices
    - map[str, str]
    - Mapping of available choices where the user choses one of the keys
      which is then converted to the value on the server side

Example:

.. code-block:: yaml

  type: choice
  choices:
    Alpha: --alpha
    Beta: --no-alpha
    Gamma: --third-option
  default: Alpha

file type
'''''''''

.. list-table::
  :header-rows: 1
  :widths: auto

  * - Key
    - Type
    - Description
  * - media-type
    - string
    - Accepted media type e.g. text/plain.
  * - media-type-parameters
    - map[str, any]
    - Auxiliary media type information/constraints.
  * - max-size
    - string
    - The maximum file size in bytes. Decimal unit prefixes are allowed.
      e.g. 1024B, 500KB or 10MB

Example:

.. code-block:: yaml

  type: file
  media-type: text/plain
  media-type-parameters:
    max-lines: 100
  max-size: 1KB


Command definition
==================

Command configuration tells Slivka how to construct the command line parameters
for the program and what environment variables should be set.
The command definition appears under ``command`` key in the service file.

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - baseCommand
    - str or array[str]
    - **Required.** A list of command line arguments appearing before any
      other parameters.
  * - inputs
    - map[str, `Input Object`_]
    - **Required.** The instructions how the form inputs are mapped to
      the command line arguments.
  * - env
    - map[str, str]
    - Environment variables that will be set for the process.
  * - arguments
    - array[str]
    - Additional arguments added after the input parameters.
  * - outputs
    - map[str, `Output Object`_]
    - **Required.** Output files produced by the command line program.


Input Object
------------
Each key (field name) specified in the inputs is linked to the 
corresponding field in the form definition.
The value provided by the user will be used to construct each command
line parameter.
If you want to add an argument which is not mapped to the
form field it is recommended to indicate it by prepending the name with
an underscore ``_`` to distinguish it from arguments taken from the input form.
Note that the value of this parameter will always be empty and will be skipped
unless a default value is provided.

Each input object corresponds to a single command line parameter passed
to the executable. They will be inserted in the order they appear in the
file skipping those having empty values.

.. list-table::
  :header-rows: 1
  :widths: auto

  * - Key
    - Type
    - Description
  * - arg
    - string
    - **Required.** Command line parameter template. Use ``$(value)``
      as the placeholder for the input value.
  * - type
    - string
    - Parameter type ensuring proper type conversion.
      One of: ``string``, ``number``, ``flag``, ``file`` or ``array``.
      Defaults to string if not specified.
  * - value
    - any
    - Default value used if no value was provided in the form.
  * - symlink
    - string
    - Name of the symlink created in the job's working directory
      pointing to the input file. Applicable with file type only.
  * - join
    - string
    - A delimiter used to join multiple values. The parameter will be
      repeated for multiple values if not specified.
      Applicable with array type only.

Each argument object have one required property ``arg`` which is a command
line argument template. Use ``$(value)`` placeholder to refer to the 
value supplied by the user in the form. You can also use environment variables 
using ``${VARIABLE}`` syntax. Additionally, a special environment variable
``SLIVKA_HOME`` pointing to the slivka project directory is available. 

If the type of the parameter is other than string, you must specify 
``type`` parameter to ensure proper value conversion. Optionally you 
may add ``value`` property if you need to specify a default value.
This value will be used if the field was not given in the form. 
It's expecially useful when defining constant command line arguments.

Here is an exmaple configuration of the command line program
*json-converter* taking two options ``--in-format`` and ``--out-format``
and input file argument, with the corresponding form 
having ``file``, ``inputformat`` and ``outputformat`` fields:

.. code-block:: yaml

  baseCommand:
  - json-converter

  inputs:
    inputformat:
      arg: --in-format=$(value)
      type: string
    outputformat:
      arg: --out-format=$(value)
      type: array
      join: ","
    file:
      arg: $(value)
      type: file
      symlink: input.txt


For the following input parameters:

- ``file: /home/slivka/media/input.json``
- ``inputformat: xml``
- ``outputformat: [yaml, json]``

The constructed command line is ::

  json-converter --in-format=xml --out-format=yaml,json input.txt

and */home/slivka/media/input.json* is automatically symlinked to
*/job/working/directory/input.txt*

.. warning::
  **Never** write a service which executes code received from an 
  untrusted source. One example is to run user provided text as
  a shell command:

  .. code-block:: yaml

    baseCommand: sh
    inputs:
      command:
        arg: -c $(value)
  

Output Object
-------------

Output objects describe individual files or groups of files created by the
command line program. Each output object have the following properties:

============ ====== =======================================================
 Field Name   Type   Description
============ ====== =======================================================
path         string **Required.** Path to the output file relative to the
                    job's working directory. Glob patterns are supported.
media-type   string Media (mime) type of the file.
============ ====== =======================================================

The standard output and standard error are redirected to *stdout* and
*stderr* respectively so these names may be used to fetch the content of
the standard output and error streams respectively.
The paths are evaluated lazily whenever the output files are requested and match
as many files as possible. Every defined result file is treated as optional
and its absence on job completion does not raise any error.

Example:

.. code-block:: yaml

  outputs:
    output:
      path: outputfile.xml
      media-type: application/xml
    auxiliary:
      path: "*_aux.json"
      media-type: application/json
    log:
      path: stdout
      media-type: text/plain
    error-log:
      path: stderr
      media-type: text/plain


.. warning::
  Patterns starting with a special characters must be quoted.


Runners
=======

So far, the configuration regarded the construction of command line arguments.
The ``runners`` define how these commands are executed on the system.
Each key in the runners section is the name of the runner and the value
is an object having following fields:

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - class
    - string
    - **Required.** A name of a built-in runner type or a path to the class
      extending the ``slivka.scheduler.Runner`` interface.
      Currently available runners are ``SlivkaQueueRunner`` and
      ``GridEngineRunner``
  * - parameters
    - map[str, any]
    - Additional parameters passed to the runner. Available parameters
      depend on the runner constructor.

Example:

.. code-block:: yaml

  runners:
    default:
      class: SlivkaQueueRunner
    grid_engine:
      class: GridEngineRunner
      parameters:
        qsub_args:
        - -P
        - webservices
        - -q
        - 64bit-pri.q
        - -l
        - ram=3400M


For non-advanced users it's recommended to set the default runner to
``SlivkaQueueRunner`` which takes no additional parameters.
``GridEngineRunner`` takes one parameter -- ``qsub_args`` -- containing
the list of arguments passed directly to the qsub command.

Limiter
=======

Limiter allows controlling the selection of the runner based on the input
parameters. The value should be a path to the class extending
``slivka.scheduler.Limiter``. The usage of limiters is covered in
the `advanced usage`_

.. _`advanced usage`: advanced_usage.html#limiters

Presets
=======

It is possible to pre-define commonly used sets of parameters to provide users
with frequently used parameters combinations using ``presets`` property
containing the list of preset objects defined below.

.. list-table::
  :widths: auto
  :header-rows: 1

  * - Key
    - Type
    - Description
  * - id
    - string
    - **Required.** Unique preset identifier.
  * - name
    - string
    - **Required.** Short name of the preset.
  * - description
    - string
    - More detailed description of the parameters set.
  * - values
    - map[str, any]
    - **Required.** Pre-configured form values.


.. note::
  The presets serve as a hint for the users only and the use of the
  pre-defined values is not enforced or checked in any way.


=====================
Launching the Project
=====================

Slivka consists of three components: RESTful HTTP server, job 
scheduler (dispatcher) and a simple worker queue running jobs
on the local machine.
The separation allows to run those parts independently of each other.
In situaitions when the scheduler is down, the server keeps collecting
the requests stashing them in the database, so when the scheduler is working
again it can catch up with the server and dispatch all pending requests.
Similarly, when the server is down, the currently submitted jobs 
are unaffected and can still be processed.

Each component can be started using ``slivka`` executable created during
Slivka package installation.

.. warning:: 
  Before you start, make sure that you have access to the running mongodb
  server which is required but is not part of slivka package.

-----------
HTTP Server
-----------

Slivka server can be started form the directory containing settings file with: 

.. code-block::

  slivka start server --type gunicorn

This will start a gunicorn using default settings specified in the
*settings.yaml* file.

Full command line specification is:

.. code-block:: sh

  slivka start [--home SLIVKA_HOME] server \
    [--type TYPE] [--daemon/--no-daemon] [--pid-file PIDFILE] \
    [--workers WORKERS] [--http-socket SOCKET]

.. list-table::
  :header-rows: 1
  :widths: auto
  
  * - Parameter
    - Description
  * - ``SLIVKA_HOME``
    - Path to the configurations directory.
      Alternatively a SLIVKA_HOME environment variable can be set.
      If neither is set, the current working directory is used.
  * - ``TYPE``
    - The wsgi application used to run the server. Currently available
      options are: gunicorn, uwsgi and devel. Using devel is discouragd
      in production as it can serve one client at the time and may
      potentially leak sensitive data.
  * - ``--daemon/--no-daemon``
    - Whether the process should be daemonised on startup.
  * - ``PIDFILE``
    - Path to the file where pid will be written to.
  * - ``WORKERS``
    - Number of serwer processes spawned on startup. Not applicable to
      the development server.
  * - ``SOCKET``
    - Specify the socket the server will accept connection from
      overriding the value from the settings file.

If you want to have more control or decided to use different wsgi
application to run the server, you can use *wsgi.py* script provided
in the project directory which contains wsgi compatible applicaiton
(see `PEP 3333`).
Here is an alternative way of starting slivka server with gunicorn
which should work with other wsgi middleware as well. ::

  gunicorn -b 0.0.0.0:8000 -w 4 -n slivka-http wsgi

.. _`PEP 3333`: https://www.python.org/dev/peps/pep-3333/

---------
Scheduler
---------

Slivka scheduler can be started using ::

  slivka start scheduler

The full command line specification:

.. code-block:: sh

  slivka start [--home SLIVKA_HOME] scheduler \
    [--daemon/--no-daemon] [--pid-file PIDFILE]

.. list-table::
  :header-rows: 1
  :widths: auto
  
  * - Parameter
    - Description
  * - ``SLIVKA_HOME``
    - Path to the configurations directory.
      Alternatively a SLIVKA_HOME environment variable can be set.
      If neither is set, the current working directory is used.
  * - ``--daemon/--no-daemon``
    - Whether the process should be daemonised on startup.
  * - ``PIDFILE``
    - Path to the file where pid will be written to.

-----------
Local Queue
-----------

The local queue can be started with ::

  slivka start local-queue

The full command line specification:

.. code-block:: sh

  slivka start [--home SLIVKA_HOME] local-queue \
    [--daemon/--no-daemon] [--pid-file PIDFILE]
 
.. list-table::
  :header-rows: 1
  :widths: auto
  
  * - Parameter
    - Description
  * - ``SLIVKA_HOME``
    - Path to the configurations directory.
      Alternatively a SLIVKA_HOME environment variable can be set.
      If neither is set, the current working directory is used.
  * - ``--daemon/--no-daemon``
    - Whether the process should be daemonised on startup.
  * - ``PIDFILE``
    - Path to the file where pid will be written to.

-------------------
Stopping Components
-------------------

To stop any of these processes, send the ``SIGINT`` (2) "interrupt" or
``SIGTERM`` (15) "terminate" signal to the process or press **Ctrl + C**
to send ``KeyboardInterrupt`` to the current process.

