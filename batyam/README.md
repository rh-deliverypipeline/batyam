## Instructions

> Please note only python 3 is supported

1. Create a new virtual env 
2. Install the packages from requirements.txt
3. cd to batyam directory (where manage.py is located)
4. '''python manage.py runserver'''

The DB should now be viewable from: http://127.0.0.1:8000/database/

For altering the data currently present in the DB,
make your changes to 'simple_data.json', and run the following command:
'''python manage.py loaddata tests/testdata/simple_data.json'''

Now just run the server again to see your chages.
