import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


def send_email(
    to_email: str, subject: str, html_content: str, sender_email: str, sender_name: str
):
    """
    Send email using SendGrid.

    Parameters:
        to_email: recipient email
        subject: email subject
        html_content: email HTML body
        sender_email: organization email (verified in SendGrid)
        sender_name: organization name
    """

    # Create the SendGrid message using organization email
    message = Mail(
        from_email=(sender_email, sender_name),
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

    except Exception as e:
        raise
