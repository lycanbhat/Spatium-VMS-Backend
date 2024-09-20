# utils/brevo_utils.py

from sib_api_v3_sdk import Configuration, ApiClient
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail, CreateSmtpEmail
from django.conf import settings

def send_brevo_email(subject, body, to_emails):

    from_email = "no-reply@spatiumoffices.com"
    from_name = "Spatium Offices"
    configuration = Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    
    api_client = ApiClient(configuration)
    
    try:
        api_instance = TransactionalEmailsApi(api_client)
        
        send_smtp_email = SendSmtpEmail(
            to=[{"email": email} for email in to_emails],
            sender={"email": from_email, "name": from_name},
            subject=subject,
            html_content=body
        )
        
        # Send the email using Brevo API
        response = api_instance.send_transac_email(send_smtp_email)
        
        # Check the response status or other indicators to determine success or failure
        if isinstance(response, CreateSmtpEmail):
            # Assuming success based on receiving CreateSmtpEmail object
            return True, "Email sent successfully"
        else:
            print(response)
            # Handle other cases where response indicates failure
            return False, f"Failed to send email. Response: {response}"
    
    except Exception as e:
        error_message = f"Error sending email: {str(e)}"
        print(error_message)
        return False, error_message
    
    finally:
        if api_client:
            api_client.pool.close()  # Adjust based on SDK specifics
