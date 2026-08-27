from dotenv import load_dotenv
from flask import json
from google import genai
import os

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






def generate_personalized_quiz(
    student_class,
    tasks,
    schedule,
    question_count=10
):

    prompt = f"""
You are Study_Mate, an AI educational assistant.

Create a personalized school quiz for a student.

Student class:
{student_class}

Recently completed study tasks:
{json.dumps(tasks, indent=2)}

Upcoming/recent study schedule:
{json.dumps(schedule, indent=2)}

Requirements:

1. Generate exactly {question_count} multiple-choice questions.
2. Questions MUST be based only on subjects/topics appearing in the supplied tasks or schedule.
3. Do not introduce unrelated subjects.
4. Give extra priority to topics the student recently completed.
5. Include multiple subjects when multiple subjects are available.
6. Difficulty should be appropriate for class {student_class}.
7. Questions should test understanding, not just memorization.
8. Every question must have exactly 4 options.
9. There must be exactly one correct answer.
10. Do not repeat questions.
11. Return valid JSON only.
12. Do not use Markdown.
13. Do not include explanations in the generated quiz.

Return exactly this structure:

{{
    "title": "Your Personalized Study Quiz",
    "description": "A quiz based on your recent Study_Mate activity.",
    "questions": [
        {{
            "subject": "Mathematics",
            "topic": "Algebraic Expressions",
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": 0
        }}
    ]
}}

The "answer" field must be the zero-based index
of the correct option.
"""


    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    text = response.text.strip()


    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()


    quiz = json.loads(text)


    if "questions" not in quiz:
        raise ValueError(
            "Gemini returned an invalid quiz."
        )


    return quiz