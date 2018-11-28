# Project 1: Japanese Learning Application

Learning languages is difficult. Language courses have high attrition rate and people generally have trouble maintaining progress. In particular, Japanese features thousands of complex characters known as kanji that are difficult to write and remember the meaning of, taking learners many years to master. This application aims to help users read more web pages by displaying information about the kanji and words contained in some text.

## Getting Started

There are two ways to run the application, through the virtual instance or local machine.

### To run from VM instance (if it is turned on)

Have a working web browser such as firefox or chrome
Enter in the following URL
```
35.237.128.17:8111
```

### To run locally

Install python

Install pip if needed
```
sudo apt-get install python-pip
```

Install libraries	
```
pip install click flask sqlalchemy statistics os
```

Run it in the shell
```
python server.py
```

Get help:
```
python server.py --help
```

## Using the App

There are many functionalities and features implemented in the application

### Home Page

At the home page, enter any word, sentence, paragraph, or text containing Japanese in the search bar, and enter search get results.

### About Page

Detailed explanation on the purpose and functionalities of the project.

### Analysis Page

Gives detailed analysis and bits of interesting trivia about search requests.

### User Account

Maintains search history of logged in user.

### Comments

Forum pulling most recent comments from all users. Contains form box to submit new comment

### Account Management (Login, Logout, Register)

Allows users to register and account by username, and login and logout using said username.


## Authors

* **Michael Wiley** - github: [mw3239](https://github.com/mw3239) - email: [tw2686@columbia.edu](tw2686@columbia.edu)
* **James Wong** - github: [tw2686](https://github.com/tw2686) - email: [tw2686@columbia.edu] (tw2686@columbia.edu) 

## Acknowledgments

* Eugene Wu - Instructor for COMS W4111 Introduction to Databases
* Felipe Rocha - IA

