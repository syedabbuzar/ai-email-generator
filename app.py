import os
import smtplib
import logging

from flask import Flask, render_template, request

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

# ==========================================
# LOAD ENV VARIABLES
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ==========================================
# FLASK APP
# ==========================================

app = Flask(__name__)

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================
# AI EMAIL AGENT
# ==========================================

email_agent = Agent(
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    ),
    markdown=False,
    description="Professional AI Email Generator"
)

# ==========================================
# GENERATE EMAIL
# ==========================================

def generate_email(name, course, start_date):

    prompt = f"""
    Write a professional internship welcome email.

    Student Name: {name}
    Course: {course}
    Internship Start Date: {start_date}

    Requirements:

    - Professional tone
    - Friendly tone
    - Proper paragraph formatting
    - No hashtags
    - No markdown
    - Bold important points using HTML <b> tags
    - Mention learning opportunities
    - End with motivation
    - Add only one Best Regards section
    - End with:

    Best Regards,
    Mellowmoon Softtech PVT LTD
    """

    try:

        response = email_agent.run(prompt)

        email_text = response.content

        return email_text

    except Exception as e:

        logging.error(f"AI generation failed: {e}")

        return f"""
        Dear <b>{name}</b>,<br><br>

        Welcome to <b>Mellowmoon Softtech PVT LTD</b>.<br><br>

        We are excited to have you onboard for the <b>{course}</b> internship starting from <b>{start_date}</b>.<br><br>

        During this internship, you will work on real-world projects, improve your practical skills, and gain valuable industry experience.<br><br>

        We wish you a successful learning journey ahead.<br><br>

        Best Regards,<br>
        Mellowmoon Softtech PVT LTD
        """

# ==========================================
# SEND EMAIL
# ==========================================

def send_email(receiver_email, subject, body):

    try:

        message = MIMEMultipart()

        message["From"] = EMAIL_USER
        message["To"] = receiver_email
        message["Subject"] = subject

        html_body = f"""
        <html>
        <body style="
            font-family: Arial;
            line-height: 1.8;
            font-size: 15px;
            color: #333333;
        ">
            {body}
        </body>
        </html>
        """

        message.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(EMAIL_USER, EMAIL_PASS)

        server.sendmail(
            EMAIL_USER,
            receiver_email,
            message.as_string()
        )

        server.quit()

        logging.info(f"Email sent successfully to {receiver_email}")

        return True

    except Exception as e:

        logging.error(f"Email sending failed: {e}")

        return False

# ==========================================
# ROUTES
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    message = ""

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        start_date = request.form["start_date"]

        ai_email = generate_email(
            name,
            course,
            start_date
        )

        success = send_email(
            receiver_email=email,
            subject="Welcome To Internship Program - Mellowmoon Softtech PVT LTD",
            body=ai_email
        )

        if success:
            message = "✅ Email Sent Successfully"
        else:
            message = "❌ Failed To Send Email"

    return render_template(
        "index.html",
        message=message
    )

# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)