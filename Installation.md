# Installation Instructions for KU Polls

1. Clone the repository
   ```
   git clone https://github.com/pannlnwza/ku-polls.git
   ```
2. Change directory into the repo
   ```
   cd ku-polls
   ```

3. Activate the virtual environment using one of the following commands, depending on your operating system

    ```shell
    python -m venv env
    ```
    - **Windows**
    
      ```shell
      env\Scripts\activate
      ```
    
    - **macOS/Linux**
    
        ```shell
        source env/bin/activate
        ```

4. Install the required packages using pip
   ```shell
   pip install -r requirements.txt
   ```
   
5. Create the .env file by copying the contents of sample.env
   - **macOS/Linux**
     ```shell
     cp sample.env .env
     ```
   - **Windows**
     ```shell
     copy sample.env .env
     ```
     You can edit the .env file to set any environment-specific values as needed.


6. Run migrations
   ```shell
   python manage.py migrate
   ```
   
7. Load fixture data
   ```shell
   python manage.py loaddata data/polls-v4.json data/users.json data/votes-v4.json
   ```
   Note: If you don't need the poll questions or users data you don't have to load the data.
   

8. Run tests
   ```shell
   python manage.py test
   ```
   
9. Start the Django server
   ```shell
   python manage.py runserver
   ```