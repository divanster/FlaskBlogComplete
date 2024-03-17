import pytz
import logging
# from datetime import datetime
#
# def get_local_time(utc_dt, tz_name):
#     if not tz_name:
#         return "Timezone unavailable"
#
#     try:
#         # Get the user's timezone
#         user_tz = pytz.timezone(tz_name)
#     except pytz.exceptions.UnknownTimeZoneError:
#         # Log or handle the specific error
#         logging.error(f"Invalid timezone: {tz_name}")
#         return "Invalid timezone"
#
#     try:
#         # Convert the UTC datetime to the user's local time
#         return utc_dt.astimezone(user_tz)
#     except ValueError:
#         # Handle the case where the datetime is "Naive"
#         # You might want to provide a default timezone here
#         logging.error("Provided UTC datetime is naive")
#         return "Invalid UTC datetime"


def get_local_time(utc_dt):
    if not utc_dt:
        # Handle case where datetime is None
        return "Datetime unavailable"
    try:
        tz = pytz.timezone('UTC')
        localized_time = utc_dt.astimezone(tz)
        return localized_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except pytz.exceptions.UnknownTimeZoneError:
        # Log or handle the specific error
        logging.error(f"Invalid timezone: {tz_name}")
        return "Invalid timezone"
