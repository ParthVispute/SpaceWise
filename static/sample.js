const form = document.querySelector("form");
const questionInput = document.querySelector("#question");
const answer = document.querySelector("#answer");
const sources = document.querySelector("#sources");
const quizButton = document.querySelector("#quiz-button");
const quiz = document.querySelector("#quiz");
const submitQuiz = document.querySelector("#submit-quiz");
const quizResult = document.querySelector("#quiz-result");
let currentQuiz = null;
let currentAnswer = [];

form.addEventListener("submit", async function(event) {

    event.preventDefault();

    const question = questionInput.value;

    answer.textContent = "Thinking...";

    sources.innerHTML = "<li>Searching for sources...</li>";


    const response = await fetch("/ask", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            question: question
        })
    });


    const data = await response.json();
    currentAnswer = data.answer;

    // Display the AI answer

   answer.innerHTML = "";

const points = document.createElement("ul");

data.answer.forEach(function(point) {

    const item = document.createElement("li");

    item.textContent = point;

    points.appendChild(item);

});

answer.appendChild(points);

    // Clear old sources

    sources.innerHTML = "";


    // Display new sources

    data.sources.forEach(function(source) {

        const item = document.createElement("li");

        const link = document.createElement("a");

        link.href = source.url;
        link.textContent = source.title;
        link.target = "_blank";

        item.appendChild(link);

        sources.appendChild(item);

    });

});

quizButton.addEventListener("click", async function() {

    quiz.innerHTML = "Generating quiz...";

    const explanation = answer.textContent;
    const question = questionInput.value;

    const response = await fetch("/quiz", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            question: question,
            explanation: explanation
        })

    });

    const data = await response.json();

    currentQuiz = data;

    quiz.innerHTML = "";
    quizResult.innerHTML = "";

    submitQuiz.style.display = "block";

    data.questions.forEach(function(q, index) {

        const container = document.createElement("div");

        const title = document.createElement("h3");

        title.textContent =
            (index + 1) + ". " + q.question;

        container.appendChild(title);


        q.options.forEach(function(option, optionIndex) {

            const label = document.createElement("label");

            const radio = document.createElement("input");

            radio.type = "radio";
            radio.name = "question" + index;
            radio.value = optionIndex;

            label.appendChild(radio);
            label.appendChild(
                document.createTextNode(" " + option)
            );

            container.appendChild(label);
            container.appendChild(
                document.createElement("br")
            );

        });


        quiz.appendChild(container);

    });

});

submitQuiz.addEventListener("click", function() {

    if (!currentQuiz) {
        return;
    }

    let score = 0;

    currentQuiz.questions.forEach(function(q, index) {

        const selected = document.querySelector(
            'input[name="question' + index + '"]:checked'
        );

        if (selected) {

            const selectedAnswer = Number(selected.value);

            if (selectedAnswer === q.answer) {
                score++;
            }
        }
    });

    quizResult.innerHTML =
        "<h3>Your Score: " +
        score +
        " / " +
        currentQuiz.questions.length +
        "</h3>";


    currentQuiz.questions.forEach(function(q, index) {

        const selected = document.querySelector(
            'input[name="question' + index + '"]:checked'
        );

        const result = document.createElement("p");

        if (selected &&
            Number(selected.value) === q.answer) {

            result.textContent =
                "Question " + (index + 1) + ": Correct ✓";

        } else {

            result.textContent =
                "Question " + (index + 1) +
                ": Incorrect ✗ — Correct answer: " +
                q.options[q.answer];
        }

        quizResult.appendChild(result);
    });

});