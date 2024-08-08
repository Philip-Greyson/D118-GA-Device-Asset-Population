# # D118-GA-Device-Asset-Population

Script to populate the asset ID field of devices in Google Admin from a spreadsheet of serial numbers and asset IDs. Column names and delimiter are customizable so the spreadsheet shouldn't need to be changed much from any other upload use.

## Overview

This script is a pretty simple one that will update devices inside of Google Admin with an asset ID, based on a spreadsheet input with serial numbers and the asset IDs to be used. This allows for asset tags to be applied and scanned alongside the device serial numbers, and then the devices to be updated in mass so that they can be searched by those asset IDs. The script takes input from a .csv, though the delimiter can be changed as long as the format is generally plaintext with a linebreak between entries. The script first compiles a list of all devices in Google Admin to store their serial number and internal device ID into a dictionary, then the input file is iterated through one line at a time, and the device ID matching the serial number for that device is updated with the specified asset ID.

## Requirements

The following Python libraries must be installed on the host machine (links to the installation guide):

- [Python-Google-API](https://github.com/googleapis/google-api-python-client#installation)

In addition, an OAuth credentials.json file must be in the same directory as the overall script. This is the credentials file you can download from the Google Cloud Developer Console under APIs & Services > Credentials > OAuth 2.0 Client IDs. Download the file and rename it to credentials.json. When the program runs for the first time, it will open a web browser and prompt you to sign into a Google account that has the permissions to update the devices. Based on this login it will generate a token.json file that is used for authorization. When the token expires it should auto-renew unless you end the authorization on the account or delete the credentials from the Google Cloud Developer Console. One credentials.json file can be shared across multiple similar scripts if desired.
There are full tutorials on getting these credentials from scratch available online. But as a quickstart, you will need to create a new project in the Google Cloud Developer Console, and follow [these](https://developers.google.com/workspace/guides/create-credentials#desktop-app) instructions to get the OAuth credentials, and then enable APIs in the project (the Admin SDK API is used in this project).

For spreadsheet requirements, the first is that your spreadsheet does have a header row for its data, otherwise you will have to just use the first device information and it will skip that device but do the rest.
The other is that each field should **not** be surrounded in quotes. If your data is such that it is going to include the delimiter character inside the field, you will either need to change the data or modify the script to process the surrounding quotes.

## Customization

The main things you should customize relate to the input spreadsheet info:

- `INPUT_FILE_NAME` is the full file name of the input spreadsheet. If it is not located in the same directory as the script, you will need to put the full path as well as the file name.
- `ASSET_COLUMN_NAME` is the column name (IE the text in the first row, the header) for the asset ID information column.
- `SERIAL_COLUMN_NAME` is the column name for the serial number column.
- `DELIMITER_CHAR` is the delimiter character between fields/columns. For a .csv, this is usually a comma, but you could use pipes, tabs, etc.

The only other thing you might want to change is the `deviceQuery` string, if all your devices are going to fit a certain criteria, as this will make the initial compilation of all the devices much quicker. For example, if all your devices were enrolled by one user, you could search for that user, or if they are all in a certain Organizational Unit you could only search for devices in that OU.
