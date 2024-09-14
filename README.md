## KU Polls: Online Survey Questions 
[![Django CI](https://github.com/pannlnwza/ku-polls/actions/workflows/django.yml/badge.svg)](https://github.com/pannlnwza/ku-polls/actions/workflows/django.yml)


An application to conduct online polls and surveys based
on the [Django Tutorial project](https://docs.djangoproject.com/en/4.1/), with
additional features.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).


## Installation

Check the instruction [here](./Installation.md).

## Running the Application

Activate the virtual environment using one of the following commands, depending on your operating system:

```shell
python -m venv env
```
- **Windows:**

  ```bash
  env\Scripts\activate
  ```

- **macOS/Linux:**

    ```bash
    source env/bin/activate
    ```

Once the virtual environment is activated, install the required packages using pip:
```bash
pip install -r requirements.txt
```

Load the poll data from file:
```bash
python manage.py loaddata data/<filename>
```

Start the Django development server (Access the web browser at <http://localhost:8000>.)
```bash
python manage.py runserver
 ```


To exit the virtual environment type:
   ```bash
   deactivate
   ```

## Demo User Accounts
| Username | Password |
|----------|----------|
| demo1    | hackme11 |
| demo2    | hackme22 |
| demo3    | hackme33 |

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).

- [Vision and Scope](../../wiki/Vision%20and%20Scope)
- [Requirements](../../wiki/Requirements)
- [Project Plan](../../wiki/Project%20Plan)
- [Domain Model](../../wiki/Domain%20Model)

- Iteration Plans
  - [Iteration 1 Plan](../../wiki/Iteration%201%20Plan)
  - [Iteration 2 Plan](../../wiki/Iteration%202%20Plan)
  - [Iteration 3 Plan](../../wiki/Iteration%203%20Plan)
  - [Iteration 4 Plan](../../wiki/Iteration%204%20Plan)

  
