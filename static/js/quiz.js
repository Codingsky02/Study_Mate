document.addEventListener("DOMContentLoaded", () => {

    const introSection = document.getElementById("quiz-intro");
    const loadingSection = document.getElementById("quiz-loading");
    const quizSection = document.getElementById("quiz-section");
    const submitLoading = document.getElementById("submit-loading");
    const resultsSection = document.getElementById("results-section");

    const generateButton = document.getElementById("generate-btn");
    const nextButton = document.getElementById("next-btn");
    const previousButton = document.getElementById("previous-btn");
    const retryButton = document.getElementById("retry-btn");

    const introMessage = document.getElementById("intro-message");
    const questionError = document.getElementById("question-error");

    const questionText = document.getElementById("question-text");
    const questionSubject = document.getElementById("question-subject");
    const questionTopic = document.getElementById("question-topic");

    const optionsContainer = document.getElementById("options-container");

    const currentQuestionElement =
        document.getElementById("current-question");

    const totalQuestionsElement =
        document.getElementById("total-questions");

    const progressBar =
        document.getElementById("progress-bar");

    const quizTitle =
        document.getElementById("quiz-title");

    const quizDescription =
        document.getElementById("quiz-description");


    let quizData = null;
    let currentQuestionIndex = 0;

    /*
     * Stores the user's selected answer.
     *
     * Example:
     *
     * answers[0] = 2
     * answers[1] = 0
     *
     * The keys represent question indexes.
     */
    let answers = {};


    /* =====================================================
       UTILITY FUNCTIONS
    ===================================================== */

    function show(element) {
        element.classList.remove("hidden");
    }


    function hide(element) {
        element.classList.add("hidden");
    }


    function showError(element, message) {

        element.textContent = message;

        show(element);
    }


    function clearError(element) {

        element.textContent = "";

        hide(element);
    }


    /* =====================================================
       GENERATE QUIZ
    ===================================================== */

    async function generateQuiz() {

        clearError(introMessage);

        hide(introSection);
        hide(resultsSection);

        show(loadingSection);

        generateButton.disabled = true;

        try {

            const response = await fetch(
                "/api/quiz/generate",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );


            const data = await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Unable to generate quiz."
                );

            }


            /*
             * Gemini returned no questions.
             *
             * This normally means the student has not
             * completed enough tasks or has no schedule.
             */

            if (
                !data.questions ||
                data.questions.length === 0
            ) {

                show(introSection);

                showError(
                    introMessage,
                    data.message ||
                    "Not enough study activity to generate a quiz."
                );

                return;
            }


            /*
             * Store the entire Gemini-generated quiz.
             */

            quizData = data;

            currentQuestionIndex = 0;

            answers = {};


            quizTitle.textContent =
                data.title ||
                "Your Personalized Quiz";


            quizDescription.textContent =
                data.description ||
                "Generated from your Study_Mate activity.";


            totalQuestionsElement.textContent =
                data.questions.length;


            hide(loadingSection);

            show(quizSection);


            renderQuestion();


        } catch (error) {

            console.error(
                "Quiz generation error:",
                error
            );

            hide(loadingSection);

            show(introSection);

            showError(
                introMessage,
                error.message ||
                "Something went wrong while generating your quiz."
            );

        } finally {

            generateButton.disabled = false;

        }

    }


    /* =====================================================
       RENDER QUESTION
    ===================================================== */

    function renderQuestion() {

        clearError(questionError);


        if (
            !quizData ||
            !quizData.questions ||
            !quizData.questions.length
        ) {
            return;
        }


        const question =
            quizData.questions[currentQuestionIndex];


        /*
         * Display question metadata.
         */

        questionSubject.textContent =
            question.subject ||
            "General";


        questionTopic.textContent =
            question.topic ||
            "Study Topic";


        questionText.textContent =
            question.question ||
            "Question unavailable.";


        /*
         * Update question counter.
         */

        currentQuestionElement.textContent =
            currentQuestionIndex + 1;


        totalQuestionsElement.textContent =
            quizData.questions.length;


        /*
         * Update progress bar.
         */

        const progress =
            (
                (currentQuestionIndex + 1) /
                quizData.questions.length
            ) * 100;


        progressBar.style.width =
            `${progress}%`;


        /*
         * Remove old options.
         */

        optionsContainer.innerHTML = "";


        /*
         * Gemini should return exactly four options.
         */

        const options =
            Array.isArray(question.options)
                ? question.options
                : [];


        options.forEach(
            (option, optionIndex) => {

                const optionElement =
                    document.createElement("button");


                optionElement.type =
                    "button";


                optionElement.className =
                    "option";


                /*
                 * If the user previously selected
                 * this answer, restore it.
                 */

                if (
                    answers[currentQuestionIndex] ===
                    optionIndex
                ) {

                    optionElement.classList.add(
                        "selected"
                    );

                }


                const letter =
                    document.createElement("span");


                letter.className =
                    "option-letter";


                letter.textContent =
                    String.fromCharCode(
                        65 + optionIndex
                    );


                const text =
                    document.createElement("span");


                text.className =
                    "option-text";


                text.textContent =
                    option;


                optionElement.appendChild(
                    letter
                );


                optionElement.appendChild(
                    text
                );


                optionElement.addEventListener(
                    "click",
                    () => {

                        selectOption(
                            optionIndex
                        );

                    }
                );


                optionsContainer.appendChild(
                    optionElement
                );

            }
        );


        updateNavigationButtons();

    }


    /* =====================================================
       SELECT OPTION
    ===================================================== */

    function selectOption(optionIndex) {

        answers[currentQuestionIndex] =
            optionIndex;


        const options =
            document.querySelectorAll(
                ".option"
            );


        options.forEach(
            (option, index) => {

                option.classList.toggle(
                    "selected",
                    index === optionIndex
                );

            }
        );


        clearError(questionError);


        updateNavigationButtons();

    }


    /* =====================================================
       NAVIGATION BUTTONS
    ===================================================== */

    function updateNavigationButtons() {

        previousButton.disabled =
            currentQuestionIndex === 0;


        const lastQuestion =
            currentQuestionIndex ===
            quizData.questions.length - 1;


        if (lastQuestion) {

            nextButton.innerHTML =
                "Submit Quiz ✓";

        } else {

            nextButton.innerHTML =
                "Next →";

        }

    }


    /* =====================================================
       NEXT QUESTION
    ===================================================== */

    function nextQuestion() {

        /*
         * Do not allow the user to continue
         * without answering.
         */

        if (
            answers[currentQuestionIndex] ===
            undefined
        ) {

            showError(
                questionError,
                "Please select an answer before continuing."
            );

            return;
        }


        const lastQuestion =
            currentQuestionIndex ===
            quizData.questions.length - 1;


        if (lastQuestion) {

            submitQuiz();

            return;
        }


        currentQuestionIndex++;

        renderQuestion();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    /* =====================================================
       PREVIOUS QUESTION
    ===================================================== */

    function previousQuestion() {

        if (currentQuestionIndex <= 0) {
            return;
        }


        currentQuestionIndex--;

        renderQuestion();


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    /* =====================================================
       SUBMIT QUIZ
    ===================================================== */

    async function submitQuiz() {

        /*
         * Make sure every question has an answer.
         */

        const totalQuestions =
            quizData.questions.length;


        for (
            let i = 0;
            i < totalQuestions;
            i++
        ) {

            if (answers[i] === undefined) {

                currentQuestionIndex = i;

                renderQuestion();

                showError(
                    questionError,
                    "Please answer this question before submitting."
                );

                return;
            }

        }


        hide(quizSection);

        show(submitLoading);


        try {

            const response = await fetch(
                "/api/quiz/submit",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        quiz_id:
                            quizData.quiz_id,

                        answers: answers

                    })
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Unable to submit quiz."
                );

            }


            displayResults(data);


        } catch (error) {

            console.error(
                "Quiz submission error:",
                error
            );


            hide(submitLoading);

            show(quizSection);


            showError(
                questionError,
                error.message ||
                "Unable to submit quiz."
            );

        }

    }


    /* =====================================================
       DISPLAY RESULTS
    ===================================================== */

    function displayResults(data) {

        hide(submitLoading);

        show(resultsSection);


        document.getElementById(
            "percentage"
        ).textContent =
            `${data.percentage || 0}%`;


        document.getElementById(
            "correct-count"
        ).textContent =
            data.correct || 0;


        document.getElementById(
            "incorrect-count"
        ).textContent =
            data.incorrect || 0;


        document.getElementById(
            "total-count"
        ).textContent =
            data.total || 0;


        /*
         * Result message.
         */

        const percentage =
            data.percentage || 0;


        let message;


        if (percentage >= 90) {

            message =
                "Excellent performance. You have a strong understanding of these topics.";

        } else if (percentage >= 75) {

            message =
                "Good work. You understand most of the material, but there is still room to improve.";

        } else if (percentage >= 50) {

            message =
                "You have the basics, but some topics need more revision.";

        } else {

            message =
                "You should revisit the studied topics and try another quiz.";

        }


        document.getElementById(
            "result-message"
        ).textContent =
            message;


        renderSubjectBreakdown(
            data.subject_breakdown || {}
        );


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    /* =====================================================
       SUBJECT BREAKDOWN
    ===================================================== */

    function renderSubjectBreakdown(breakdown) {

        const container =
            document.getElementById(
                "subject-breakdown"
            );


        container.innerHTML = "";


        const subjects =
            Object.keys(breakdown);


        if (!subjects.length) {

            container.innerHTML =
                `
                <p class="small-note">
                    No subject breakdown is available.
                </p>
                `;

            return;
        }


        subjects.forEach(
            (subject) => {

                const stats =
                    breakdown[subject];


                const correct =
                    Number(
                        stats.correct || 0
                    );


                const total =
                    Number(
                        stats.total || 0
                    );


                const percentage =
                    total > 0
                        ? Math.round(
                            (correct / total) * 100
                        )
                        : 0;


                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "breakdown-item";


                item.innerHTML = `
                    <div class="breakdown-top">

                        <strong>
                            ${escapeHTML(subject)}
                        </strong>

                        <span class="breakdown-score">
                            ${correct}/${total}
                            ·
                            ${percentage}%
                        </span>

                    </div>

                    <div class="breakdown-track">

                        <div
                            class="breakdown-fill"
                            style="width: ${percentage}%"
                        ></div>

                    </div>
                `;


                container.appendChild(
                    item
                );

            }
        );

    }


    /* =====================================================
       HTML ESCAPE
    ===================================================== */

    function escapeHTML(value) {

        const div =
            document.createElement("div");


        div.textContent =
            value;


        return div.innerHTML;

    }


    /* =====================================================
       EVENT LISTENERS
    ===================================================== */

    generateButton.addEventListener(
        "click",
        generateQuiz
    );


    nextButton.addEventListener(
        "click",
        nextQuestion
    );


    previousButton.addEventListener(
        "click",
        previousQuestion
    );


    retryButton.addEventListener(
        "click",
        () => {

            hide(resultsSection);

            show(introSection);

            clearError(introMessage);

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        }
    );

});

async function generateQuiz() {
    const button = document.getElementById("generateQuizBtn");
    const loading = document.getElementById("quizLoading");
    const errorBox = document.getElementById("quizError");

    if (button) {
        button.disabled = true;
        button.textContent = "Generating...";
    }

    if (loading) {
        loading.style.display = "block";
    }

    if (errorBox) {
        errorBox.style.display = "none";
        errorBox.textContent = "";
    }

    try {
        const response = await fetch("/api/quiz/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        console.log("Quiz API response:", data);

        if (!response.ok) {
            throw new Error(
                data.error || "Failed to generate quiz."
            );
        }

        if (!data.questions || data.questions.length === 0) {
            throw new Error(
                data.message || "No quiz questions were generated."
            );
        }

        // Store generated quiz
        window.currentQuiz = data;

        // Display quiz
        displayQuiz(data);

    } catch (error) {

        console.error("Quiz generation failed:", error);

        if (errorBox) {
            errorBox.textContent = error.message;
            errorBox.style.display = "block";
        }

    } finally {

        // THIS IS CRITICAL
        if (loading) {
            loading.style.display = "none";
        }

        if (button) {
            button.disabled = false;
            button.textContent = "Generate Personalized Quiz";
        }
    }
}