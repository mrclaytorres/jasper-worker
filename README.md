# Jasper Worker

### Install Dependencies
```
$ pip install -r requirements.txt
```
### Download Chrome Webdriver
* [Download Chrome's webdriver](https://chromedriver.chromium.org/downloads) and save it on root directory.
  * Make sure you download the webdriver that's compatible with your current Google Chrome.

### Create Your Credentials
* Assuming you already have an account to Jasper.ai.
* Create a **creds.py** file in your project's root directory
  * Inside your **creds.py**, create your credentials like this:
``` 
USERNAME = 'Your email/username here'
PASSWORD = 'Your password here'
```
### Jasper Signin Code
* Jasper sends a Signin Code to your email/phone that you will have to manually input once the it prompts you.

### Create Input File
* Rename the `sample_query.csv` file to `query.csv`
* Inside the query.csv are the one input parameters
    * prompt - The prompt you input in Jasper's QL Editor.

### Create User Agent (UA) File
* Create a file called `user_agents.csv` and enter at least two lines of User Agent strings.

### Create Output Folder
* On your project's root directory, create a folder named **csvfiles**.
* The output should be inside the **csvfiles** folder

### Running The Script
```
$ python jasper.py
```