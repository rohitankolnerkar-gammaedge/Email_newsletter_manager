from app.services.send_email import send_email


def send_confirmation_email(
    to_email: str,
    confirmation_link: str,
    sender_email: str,
    sender_name: str,
):
    subject = "Confirm your subscription"

    html_content = f"""
    <h2>Confirm your subscription</h2>
    <p>Thanks for subscribing!</p>
    <p>Please confirm your email by clicking the link below:</p>
    <p>
        <a href="{confirmation_link}">
            Confirm Subscription
        </a>
    </p>
    <p>If you didn’t request this, you can safely ignore this email.</p>
    """

    send_email(
        to_email=to_email,
        subject=subject,
        html_content=html_content,
        sender_email=sender_email,
        sender_name=sender_name,
    )
