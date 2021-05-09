# Hungfung
--------------------- Flask environment -----------------------------------------------------------

In order to run the application you must have the proper environment active. To activate the environment you need to run the 'activate' file in env/Scripts/activate

Linux/Mac: source env/Scripts/activate

Windows: run the same activate file without 'source' command

---------------------- Database Initialization ------------------------------------------------------

The command to initialize the databse is:

    flask init-db
This command will create a sqlite3 database instance, from the contents of the 'Hungfun_1_final.sql' file. This instance is located in : instance/flaskr.sqlite

This command only needs to be run once when the initial database needs to be created, all subsequent querys will be run on the created instance and saved between application runs

** if you wish to run 'flask init-db' after it has already been initialised, you must first delete the current database instance **

---------------------- Run Application --------------------------------------------------------------------

With the environment activated enter: flask run

This will start the flask application on 127.0.0.1:5000
