from flask import Flask, request, jsonify, render_template
from tavily import TavilyClient
import requests
import json
import os


# ==========================================
# 1. CREATE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# 2. CONNECT TO TAVILY
# ==========================================

tavily = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)


# ==========================================
# 3. OPENROUTER SETTINGS
# ==========================================

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openrouter/free"


# ==========================================
# 4. SHOW THE HTML PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("sample.html")


# ==========================================
# 5. RECEIVE QUESTION FROM JAVASCRIPT
# ==========================================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.json

    question = data["question"]


    # ======================================
    # 6. SEARCH THE WEB USING TAVILY
    # ======================================

    search = tavily.search(
    query=f"{question} scientific explanation technical information",
    search_depth="advanced",
    max_results=5
)


    # ======================================
    # 7. PREPARE WEB INFORMATION
    # ======================================

    web_information = ""

    for result in search["results"]:

        web_information += f"""
Title: {result["title"]}
URL: {result["url"]}
Information: {result["content"]}

"""


    # ======================================
    # 8. CREATE THE PROMPT FOR THE AI
    # ======================================

    prompt = f"""
You are SpaceWise AI, a science and space education assistant.

The user asked:

{question}

Here is information retrieved from the web:

{web_information}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "answer": [
        "First short point",
        "Second short point",
        "Third short point"
    ]
}}

Rules:

- Give 5 to 6 points.
- Each point must contain exactly one main idea.
- Each point should normally be one sentence.
- Keep each point concise.
- Use simple language suitable for a student.
- Do not include markdown.
- Do not include numbering inside the points.
- Do not include any text outside the JSON.

If the question is outside science, space, astronomy,
physics, space technology, or India's space program,
return:

{{
    "answer": [
        "I can only answer science and space-related questions."
    ]
}}
"""

    # ======================================
    # 9. SEND QUESTION TO OPENROUTER
    # ======================================

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }


    body = {

        "model": MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]

    }


    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=body
    )


    # ======================================
    # 10. CHECK IF OPENROUTER RESPONDED
    # ======================================

    if response.status_code != 200:

        print("OpenRouter error:")
        print(response.text)

        return jsonify({
            "answer": "Sorry, the AI service could not answer right now.",
            "sources": []
        }), 500


    # ======================================
    # 11. GET THE AI ANSWER
    # ======================================

    result = response.json()

    raw_answer = result["choices"][0]["message"]["content"]

    answer_data = json.loads(raw_answer)

    answer = answer_data["answer"]
    # ======================================
    # 12. PREPARE SOURCES
    # ======================================

    sources = []

    for result in search["results"]:

        sources.append({
            "title": result["title"],
            "url": result["url"]
        })


    # ======================================
    # 13. SEND ANSWER + SOURCES
    #     BACK TO JAVASCRIPT
    # ======================================

    return jsonify({

        "answer": answer,

        "sources": sources

    })


# ==========================================
# QUIZ
# ==========================================

@app.route("/quiz", methods=["POST"])
def quiz():

    data = request.json

    question = data["question"]
    explanation = data["explanation"]

    prompt = f"""
Create a 5-question multiple-choice quiz based ONLY
on the following explanation.

Question:
{question}

Explanation:
{explanation}

Return ONLY valid JSON in this format:

{{
    "questions": [
        {{
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

Rules:

- Exactly 5 questions.
- Exactly 4 options per question.
- "answer" must be 0, 1, 2, or 3.
- Test understanding of the explanation.
- Do not use information outside the explanation.
- Return ONLY JSON.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=body
    )

    if response.status_code != 200:
        return jsonify({
            "error": "Quiz generation failed."
        }), 500

    result = response.json()

    raw_quiz = result["choices"][0]["message"]["content"]

    quiz_data = json.loads(raw_quiz)

    return jsonify(quiz_data)

# ==========================================
# 14. START FLASK
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)