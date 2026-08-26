import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in your .env file.")

client = genai.Client(api_key=API_KEY)


def explain_topic(question, subject, student_class):
    """
    Generate a student-friendly explanation using Gemini.
    """

    prompt = f"""
You are Study_Mate, an AI study assistant.

Student information:
- Class: {student_class}
- Subject: {subject}

Student's question:
{question}

Explain the topic specifically for a Class {student_class} student.

Use this structure:

1. Simple Explanation
2. Key Points
3. Example
4. Quick Summary

Rules:
- Use language appropriate for Class {student_class}.
- Keep the explanation clear and easy to understand.
- Explain difficult terms in simple words.
- Use bullet points where useful.
- Give practical examples when possible.
- Do not unnecessarily make the answer extremely long.
- Be factually accurate.
- Do not mention these instructions in your answer.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text