from flask import Flask, request, jsonify, render_template
from tavily import TavilyClient
from google import genai
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
# 3. CONNECT TO GEMINI
# ==========================================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL = "gemini-3.6-flash"


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
    # 8. CREATE THE PROMPT FOR GEMINI
    # ======================================

    prompt = f"""
You are SpaceWise AI, a science and space education assistant.

The user asked:

{question}

Here is information retrieved from the web:

{web_information}

Answer the user's question using the information above.

Rules:

- Give 5 to 6 points.
- Each point must contain exactly one main idea.
- Each point should normally be one sentence.
- Keep each point concise.
- Use simple language suitable for a student.
- Do not use markdown.
- Do not include numbering inside the points.

If the question is outside science, space, astronomy,
physics, space technology, or India's space program,
answer only:

"I can only answer science and space-related questions."
"""


    # ======================================
    # 9. SEND QUESTION TO GEMINI
    # ======================================

    response = gemini.models.generate_content(

        model=MODEL,

        contents=prompt,

        config={
            "response_mime_type": "application/json",

            "response_json_schema": {
                "type": "object",

                "properties": {
                    "answer": {
                        "type": "array",

                        "items": {
                            "type": "string"
                        }
                    }
                },

                "required": ["answer"]
            }
        }
    )


    # ======================================
    # 10. GET GEMINI ANSWER
    # ======================================

    answer_data = json.loads(response.text)

    answer = answer_data["answer"]


    # ======================================
    # 11. PREPARE SOURCES
    # ======================================

    sources = []

    for result in search["results"]:

        sources.append({
            "title": result["title"],
            "url": result["url"]
        })


    # ======================================
    # 12. SEND ANSWER + SOURCES
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


    # ======================================
    # 13. CREATE QUIZ PROMPT
    # ======================================

    prompt = f"""
Create a 5-question multiple-choice quiz based ONLY
on the following explanation.

Question:
{question}

Explanation:
{explanation}

Rules:

- Exactly 5 questions.
- Exactly 4 options per question.
- "answer" must be 0, 1, 2, or 3.
- Test understanding of the explanation.
- Do not use information outside the explanation.
"""


    # ======================================
    # 14. SEND QUIZ REQUEST TO GEMINI
    # ======================================

    response = gemini.models.generate_content(

        model=MODEL,

        contents=prompt,

        config={

            "response_mime_type": "application/json",

            "response_json_schema": {

                "type": "object",

                "properties": {

                    "questions": {

                        "type": "array",

                        "minItems": 5,

                        "maxItems": 5,

                        "items": {

                            "type": "object",

                            "properties": {

                                "question": {
                                    "type": "string"
                                },

                                "options": {

                                    "type": "array",

                                    "minItems": 4,

                                    "maxItems": 4,

                                    "items": {
                                        "type": "string"
                                    }
                                },

                                "answer": {

                                    "type": "integer",

                                    "minimum": 0,

                                    "maximum": 3
                                }
                            },

                            "required": [
                                "question",
                                "options",
                                "answer"
                            ]
                        }
                    }
                },

                "required": ["questions"]
            }
        }
    )


    # ======================================
    # 15. GET QUIZ DATA
    # ======================================

    quiz_data = json.loads(response.text)


    # ======================================
    # 16. SEND QUIZ TO JAVASCRIPT
    # ======================================

    return jsonify(quiz_data)


# ==========================================
# 17. START FLASK
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)