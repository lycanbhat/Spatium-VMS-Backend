from django.conf import settings

APP_NAME = settings.APPLICATION_NAME
EMAIL_LOGO = settings.EMAIL_LOGO

OTP_VERIFICATION = {
    "subject" : "Verification Code - {}".format(APP_NAME),
}

VISITOR_WAITING = {
    "subject" : "Visitor Waiting for You in the Lobby",
}

DOWNLOAD_ID = {
    "subject" : "Download Identity Card",
}

INVALID_EMAIL_FORMAT_ERROR = "Invalid email format."

EMPTY_NAME_ERROR = "Name field cannot be empty."