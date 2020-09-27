# Spine Items

Spine project items.

## Programming language

- Python 3.6
- Python 3.7

Please note that Python 3.8 is **not** supported yet.

## License

Spine Items is released under the GNU Lesser General Public License (LGPL) license. All accompanying
documentation, original graphics and other material are released under the 
[Creative Commons BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/).

## Installing Spine Items

Installing requires you to [clone](https://help.github.com/articles/cloning-a-repository/) or 
download the latest version of the source code to your computer.

The development happens on the `master` branch and all the latest features and bug fixes will be added there
first. 

The **recommended** way to install Spine Items is by using Anaconda or Miniconda environments.

Step-by-step instructions:

1. Clone the `master` branch from Spine Items repository on GitHub onto your computer. 
2. cd to Spine Items root directory (the one with requirements.txt)
3. Install requirements using **pip**

        pip install -r requirements.txt



### About requirements

Python 3.6 or Python 3.7 is required.

See file `setup.py` and `requirements.txt` for packages required to use Spine Items.

#### Upgrading Requirements

To upgrade all required packages for Spine Toolbox, run

    pip install --upgrade -r requirements.txt

You may want to do this occasionally if it has been a long time (i.e. several months) 
since you first installed the requirements.

The requirements include one package (`spinedb_api`) developed by 
the Spine project consortium. Since they are developed very actively at the moment, you 
may need to upgrade these regularly.

#### Upgrading [spinedb_api](https://github.com/Spine-project/Spine-Database-API)

The package `spinedb_api` is required for running Spine Toolbox. Whenever you 
merge the latest changes from the remote server onto your local copy of the 
application (i.e. do a `git pull`), the application may request you to upgrade 
this package. You can either do this manually or by running an upgrade script, 
which has been added for convenience.

To upgrade with a script, run `upgrade_spinedb_api.bat` on Windows or 
`upgrade_spinedb_api.py` on Linux and Mac OS X. The scripts are located in the
`bin` directory.

To upgrade manually, run

    pip install --upgrade git+https://github.com/Spine-project/Spine-Database-API.git


## Building the User Guide

Source files for the User Guide can be found in `docs/source` directory. In order to 
build the HTML docs, you need to install the *optional requirements* (see section 
'Installing requirements' above). This installs Sphinx (among other things), which 
is required in building the documentation. When Sphinx is installed, you can build the 
HTML pages from the user guide source files by using the `bin/build_doc.bat` script on 
Windows or the `bin/build_doc.sh` script on Linux and Mac. After running the script, the 
index page can be found in `docs/build/html/index.html`. The User Guide can also 
be opened from Spine Toolbox menu Help->User Guide (F2).

