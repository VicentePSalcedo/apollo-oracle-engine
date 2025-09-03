from sendgrid.helpers.mail import Mail, Asm
from .logger import log_info, log_error

def send_single_email(sg_client, email_address, html_template_path, from_email, subject, asm_group_id=None):
    """
    Sends a single test email to a specified address.

    :param email_address: The recipient's email address.
    :param html_template_path: Path to the HTML email template.
    :param from_email: The sender's email address.
    :param subject: The email subject.
    :param asm_group_id: The ID of the unsubscribe group to use.
    :param dynamic_template_data: A dictionary of dynamic data to pass to the template.
    """
    try:
        with open(html_template_path, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        log_error(f"Error: Template file not found at {html_template_path}")
        return

    log_info(f"--- Preparing to send a single test email to {email_address} ---")

    message = Mail(
        from_email=from_email,
        to_emails=email_address,
        subject=subject,
        html_content=html_content
    )
    if asm_group_id:
        message.asm = Asm(group_id=int(asm_group_id))
        message.add_personalization

    try:
        response = sg_client.send(message)
        log_info(f"  -> Sent successfully! Status code: {response.status_code}")
        log_info("  -> Check your inbox to see the test email.")
    except Exception as e:
        log_error(f"  -> Failed to send. Error: {e}\nBody: {e.body}")
