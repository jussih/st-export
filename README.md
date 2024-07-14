# Export all Sports Tracker workouts as GPX

Sports Tracker has a support request form for user data extract, but it seems
they never provide the requested data. This tool is an alternative way to back
up the entire workout history.

Usage:
- Activate a virtualenv
- `pip install -r requirements.txt`
- `python ./st-export.py --export-path <directory path to save GPX files> --token <session token>`
- session token is the value of the `STTAuthorization` header when making HTTP requests to the
  ST api when logged in to the service in a web browser
