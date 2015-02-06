#### Installation  
    $ pip install virtualenvwrapper  

Add the following to your .bashrc/.zshrc  
    export WORKON_HOME=$HOME/.virtualenvs  
    export PROJECT_HOME=$HOME/Devel  
    source /usr/local/bin/virtualenvwrapper.sh  

Create a directory for the project and a new virtual environment  
    $ mkdir 402project && cd 402project   
    $ mkvirtualenv  402project  
    $ workon 402project  

The terminal should now indicate with brackets your in the venv  
To get out of the venv  
    $ deactivate   

Download libraries  
Make sure venv is activated and install required packages with...   
    $ workon 402project  
    $ pip install -r requirements.txt  
