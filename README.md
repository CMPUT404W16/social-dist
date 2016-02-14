# social-dist

Simple instruction to start

Once you clone this repo, you need to setup the virtual environment first.

cd to the project folder (It has a file called requirements.txt)

Do
    
    virtualenv env

Waiting for the virtual environment setup process...

After the setup process finish, type

    source env/bin/activate
    
    pip install -r requirenments.txt
    
Then pip will help you get all the packages we need.

In the case of installing any new package and you want to add the package to the requirement list, you can check the package list by typing

    pip freeze
    
If you want to update the requirement.txt file, type

    pip freeze > requirements.txt
    
    