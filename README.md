# Jasper Worker (erwangse)

> This is a fork that uses a JSON file for feeding sentences to Jasper Worker.
> It also supports other helper scripts & experimental options.

## Install Dependencies
```
pip install -r requirements.txt
```
## Webdriver / Chromedriver

Jasper Worker functions by automatically controlling a browser window.
Though, to do so, you will need to download a *webdriver* that supports your installed browser version.

* [Download Chrome's webdriver](https://chromedriver.chromium.org/downloads) and save it on root directory.
  * Make sure you download the webdriver that's compatible with your current Google Chrome.

> Note: While you can download & use other drivers such as *Geckodriver* for Firefox,
> doing so is not supported.

## Credentials
Assuming you already have an account to Jasper.ai,
* Rename the `creds.json.sample` to `creds.json` file in the project's root directory, and fill in your Jasper.ai credentials.

## 2FA / Sign-in Code
* If Jasper.ai sends a Sign-in Code to your email and/or phone, you will have to manually enter it.

## Queries / Sentences
* Rename the `query.json.sample` file to `query.json` and enter in your sentences as strings.

## User Agents (UAs)
* Rename the file called `ua.json.sample` to `ua.json` and enter at least 2 User Agent strings.

## Output
* Jasper Worker will automatically save the generated prompts to a file in the `output` folder. It will be automatically generated if it doesn't exist.

## Running Jasper Worker
```
# Assuming you followed the steps above & you use a Linux-based system.
./jasper.py
```