# student-mentor-api
Student Mentor API 

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/mdaalam22/student-mentor-api.git
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python3 -m venv env
$ env/Scripts/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies:
follow the instruction mentioned in the `.env.dist`

```sh
(env)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/

