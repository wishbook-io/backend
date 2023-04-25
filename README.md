# backend
Django APIs, scripts, async jobs - python

## Key folders
1. api is the main app, with all the APIs
2. internal_scripts is the main folder for all the scripts used internally by engineering for fixes / changes, seed data, etc.
3.google_sheet, apns, picasa_secrets has some temporary credentials for google_sheet - to be skipped.

## Common config / changes
- project_settings/settings.py - common settings for django models, server, APIs, etc. Most of these fields are marked as \<TOADD\> in the checked in version. These need to be updated with the correct values.
- api/
  - serializers.py - SMTP sending service credentials (eg valuefirst)
  - changes.py - Google API key 
  - v1/
    - order/ship_rocket.py - shiprocket credentials
- internal_scripts/ - should be various scripts with hard-coded credentials.
    
