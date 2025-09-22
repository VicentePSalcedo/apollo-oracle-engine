import json
from sendgrid.helpers.mail import Mail, Asm
from .logger import log_info, log_error

def validate_email(sg_client, email_address):
    try:
        response = sg_client.client.validations.email.post(
            request_body={
                'email': email_address
            }
        )
        if response.status_code == 200:
            response_body = json.loads(response.body.decode('utf-8'))
            verdict = response_body.get('result', {}).get('verdict')
            log_info(f"Email validation for {email_address}: {verdict}")
            return verdict == 'Valid'
        else:
            log_error(f"Email validation API returned status {response.status_code} for {email_address}")
            return False
    except Exception as e:
        log_error(f"An error occurred during email validation: {e}")
        return False

def clean_company_name(company_name):
    suffixes_to_remove = {"llc", "l.l.c.", "l.l.c", "pa", "inc", "inc."}
    name_no_commas = company_name.replace(',', '')
    words = name_no_commas.split()
    if words and words[-1].lower() in suffixes_to_remove:
        words.pop() # Remove the last word
    cleaned_name = " ".join(words).strip().title()
    return cleaned_name

def personalize_email(template, business_name):
    business_name = clean_company_name(business_name)
    return template.replace("{{{Business Name}}}", business_name)

def send_single_email(sg_client, email_address, html_template_path, from_email, subject, business_name, asm_group_id=None):
    

    try:
        with open(html_template_path, 'r') as f:
            html_template = f.read()
    except FileNotFoundError:
        log_error(f"Error: Template file not found at {html_template_path}")
        exit(0)

    log_info(f"--- Preparing to send a single test email to {email_address} ---")

    html_content = personalize_email(
        template=html_template,
        business_name=business_name
    )
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
    except Exception as e:
        log_error(f"  -> Failed to send. Error: {e}\nBody: {e.body}")
        exit(0)
