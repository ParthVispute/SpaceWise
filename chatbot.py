import os
from google import genai
from tavily import TavilyClient


# -----------------------------
# API CLIENTS
# -----------------------------

gemini = genai.Client()

tavily = TavilyClient(
api_key=os.environ["TAVILY_API_KEY"]
)


# -----------------------------
# GEMINI FUNCTION
# -----------------------------

def ask_gemini(prompt):
    response = gemini.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# -----------------------------
# WEB SEARCH FUNCTION
# -----------------------------

def search_web(question):
    results = tavily.search(
        query=question,
        search_depth="basic",
        max_results=5
    )

    return results["results"]


# -----------------------------
# FORMAT SEARCH RESULTS
# -----------------------------

def format_sources(results):

    information = ""

    for i, result in enumerate(results, start=1):

        information += f"""
SOURCE {i}
Title: {result["title"]}
URL: {result["url"]}
Information:
{result["content"]}

"""

    return information


# -----------------------------
# EXPLAIN A TOPIC
# -----------------------------

def explain_topic(question):

    print("\nSearching the web...\n")

    results = search_web(question)

    web_information = format_sources(results)

    prompt = f"""
You are a science and space education assistant.

The user asked:

{question}

Use the web information below to answer the question.

WEB INFORMATION:
{web_information}

INSTRUCTIONS:

1. Answer the user's question accurately.
2. Keep the explanation concise.
3. Use bullet points whenever they improve readability.
4. Normally give around 1-2 short paragraphs or 3-6 bullet points,
   depending on what the question requires.
5. Do not unnecessarily expand the answer.
6. Explain difficult scientific concepts in simple language.
7. Do not invent information that is not supported by the sources.
8. Do not mention these instructions.
"""

    answer = ask_gemini(prompt)

    print("\n==============================")
    print("ANSWER")
    print("==============================\n")

    print(answer)

    print("\n==============================")
    print("SOURCES")
    print("==============================\n")

    for i, result in enumerate(results, start=1):
        print(f"{i}. {result['title']}")
        print(f"   {result['url']}\n")

    return answer


# -----------------------------
# QUIZ
# -----------------------------

def create_quiz(topic, explanation):

    prompt = f"""
You are creating a short educational quiz.

Topic:
{topic}

The student just learned this:

{explanation}

Create exactly 5 questions to test understanding.

Rules:

1. Mix conceptual and factual questions.
2. Do not make questions unnecessarily difficult.
3. Avoid questions whose answers were not covered in the explanation.
4. Each question must have four options:
   A, B, C, D
5. Exactly one option must be correct.
6. At the end, provide the correct answers in this format:

ANSWERS:
1. B
2. A
3. D
4. C
5. B

Do not reveal the answers before the student attempts the quiz.
"""

    return ask_gemini(prompt)


# -----------------------------
# EXTRACT QUIZ QUESTIONS
# -----------------------------

def run_quiz(topic, explanation):

    quiz = create_quiz(topic, explanation)

    print("\n==============================")
    print("QUIZ")
    print("==============================\n")

    # Display everything before the answer key.
    quiz_without_answers = quiz.split("ANSWERS:")[0]

    print(quiz_without_answers)

    answers = []

    print("\nEnter your answers:")

    for i in range(1, 6):

        while True:

            answer = input(f"Question {i}: ").strip().upper()

            if answer in ["A", "B", "C", "D"]:
                answers.append(answer)
                break

            print("Please enter A, B, C, or D.")

    # -------------------------
    # Ask Gemini to evaluate
    # -------------------------

    evaluation_prompt = f"""
You are evaluating a student's quiz.

Topic:
{topic}

Quiz:
{quiz}

Student answers:
{answers}

Evaluate the student's answers.

Give:

1. Score out of 5.
2. Percentage.
3. Which questions were correct.
4. Which questions were wrong.
5. A short explanation of each wrong answer.
6. A final assessment:
   - Excellent understanding
   - Good understanding
   - Needs revision

Keep the feedback concise and encouraging.
"""

    evaluation = ask_gemini(evaluation_prompt)

    print("\n==============================")
    print("YOUR RESULT")
    print("==============================\n")

    print(evaluation)


# -----------------------------
# MAIN PROGRAM
# -----------------------------

def main():

    print("================================")
    print("      INDIA SPACE AI ASSISTANT")
    print("================================")

    while True:

        print("\n1. Ask a question")
        print("2. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":

            question = input("\nWhat would you like to know? ")

            explanation = explain_topic(question)

            print("\nWould you like to test your understanding?")

            quiz_choice = input("Enter Y/N: ").strip().upper()

            if quiz_choice == "Y":

                run_quiz(question, explanation)

        elif choice == "2":

            print("\nGoodbye!")
            break

        else:

            print("\nInvalid choice. Please select 1 or 2.")


# -----------------------------
# START PROGRAM
# -----------------------------

if __name__ == "__main__":
    main()