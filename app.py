import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging
import traceback
import re
from streamlit_lottie import st_lottie
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuizGenerator:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.7,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile"
        )

    def generate_questions(self, topic, difficulty, num_questions=10):
        if topic == "Select Any Topic":
            prompt = PromptTemplate(
                input_variables=["num_questions", "difficulty"],
                template="""
                Generate {num_questions} professional English MCQ questions with 4 options each at a {difficulty} difficulty level.
                Each question should test various English language skills including Articles, Nouns, Pronouns, Verbs, Adjectives, Adverbs, Prepositions, Conjunctions, Interjections, Tenses, Punctuation.
                
                Format each question EXACTLY as follows:
                Question [number]:
                [Question text]
                1) [Option 1]
                2) [Option 2]
                3) [Option 3]
                4) [Option 4]
                Correct Answer: [1, 2, 3, or 4]
                
                Generate all {num_questions} questions in one response.
                Ensure all options are complete sentences without trailing dots.
                """
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            response = chain.invoke({"num_questions": num_questions, "difficulty": difficulty})
        else:
            prompt = PromptTemplate(
                input_variables=["topic", "num_questions", "difficulty"],
                template="""
                Generate {num_questions} professional English MCQ questions with 4 options each on the topic of {topic} at a {difficulty} difficulty level.
                Each question should test English language skills related to {topic}.
                
                Format each question EXACTLY as follows:
                Question [number]:
                [Question text]
                1) [Option 1]
                2) [Option 2]
                3) [Option 3]
                4) [Option 4]
                Correct Answer: [1, 2, 3, or 4]
                
                Generate all {num_questions} questions in one response.
                Ensure all options are complete sentences without trailing dots.
                """
            )
            chain = LLMChain(llm=self.llm, prompt=prompt)
            response = chain.invoke({"topic": topic, "num_questions": num_questions, "difficulty": difficulty})
        
        return response['text'].strip()

def parse_questions(questions_text):
    questions_list = []
    individual_questions = re.split(r'Question \d+:', questions_text)[1:]
    
    for question_text in individual_questions:
        try:
            question_match = re.search(r'(.+?)(?=1[\)\.]\s|\n|$)', question_text, re.DOTALL)
            options_match = re.findall(r'(\d)[\)\.]\s*(.+?)(?=\d[\)\.]\s|\n|Correct Answer|$)', question_text, re.DOTALL)
            correct_answer_match = re.search(r'Correct Answer:?\s*(\d)', question_text, re.IGNORECASE)
            
            if not all([question_match, options_match, correct_answer_match]):
                continue
                
            question = question_match.group(1).strip()
            options = {str(option[0]): option[1].strip().rstrip('.') for option in options_match}
            correct_answer = correct_answer_match.group(1)
            
            questions_list.append((question, options, correct_answer))
            logger.info(f"Generated Question: {question}")
            logger.info(f"Options: {options}")
            logger.info(f"Correct Answer: {correct_answer}")
            logger.info("---")
        except Exception as e:
            logger.error(f"Error parsing question: {str(e)}")
            continue
            
    return questions_list

def set_page_config():
    st.set_page_config(page_title="English MCQ Quiz", page_icon="📚", layout="wide")
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .main { padding: 2rem; }
        .quiz-title { 
            font-size: 2.5em;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 1em;
            font-family: 'Arial', sans-serif;
        }
        .correct { 
            color: #28a745; 
            font-weight: bold;
        }
        .incorrect { 
            color: #dc3545; 
            font-weight: bold;
        }
        .question-text { 
            font-size: 1.3em; 
            margin-bottom: 1.5em;
            padding: 1em;
        }
        .stButton button {
            width: 100%;
            background-color: #007bff;
            color: white;
            font-weight: bold;
            padding: 0.5em 1em;
        }
        .big-font {
            font-size:50px !important;
            font-weight: bold;
            color: #1E88E5;
            text-align: center;
        }
        .sub-font {
            font-size:25px !important;
            color: #424242;
            text-align: center;
        }
        .score-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .score-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .score-value {
            font-size: 48px;
            font-weight: bold;
            color: #007bff;
        }
        .score-percentage {
            font-size: 24px;
            color: #6c757d;
        }
        .footer {
            text-align: center;
            padding: 20px 0;
            font-size: 14px;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def show_welcome_screen():
    st.markdown('<p class="big-font">📚 English MCQ Quiz</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-font">Test your English language skills with our interactive quiz!</p>', unsafe_allow_html=True)

    # Add a Lottie animation
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_1pxqjqps.json"
    lottie_json = load_lottie_url(lottie_url)
    st_lottie(lottie_json, height=300, key="lottie")

    col1, col2 = st.columns(2)

    with col1:
        topics = [
            "Select Any Topic", "Articles", "Nouns", "Pronouns", "Verbs", "Adjectives", "Adverbs",
            "Prepositions", "Conjunctions", "Interjections", "Tenses", "Punctuation"
        ]
        selected_topic = st.selectbox("Choose a topic for your quiz:", topics, index=0)

    with col2:
        difficulty_levels = ["Easy", "Medium", "Hard"]
        selected_difficulty = st.selectbox("Choose a difficulty level:", difficulty_levels)

    st.markdown("<br>", unsafe_allow_html=True)

    start_button = st.button("Start Quiz 🚀")

    return start_button, selected_topic, selected_difficulty

def quiz_interface():
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        
    if not st.session_state.quiz_started:
        start_quiz, selected_topic, selected_difficulty = show_welcome_screen()
        if start_quiz:
            st.session_state.quiz_started = True
            st.session_state.selected_topic = selected_topic
            st.session_state.selected_difficulty = selected_difficulty
            st.rerun()
            
    else:
        if 'quiz_generator' not in st.session_state:
            st.session_state.quiz_generator = QuizGenerator()
        
        if 'questions' not in st.session_state:
            with st.spinner("Generating questions..."):
                st.session_state.questions = []
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                
                questions_text = st.session_state.quiz_generator.generate_questions(
                    st.session_state.selected_topic,
                    st.session_state.selected_difficulty,
                    10
                )
                st.session_state.questions = parse_questions(questions_text)
                
                if len(st.session_state.questions) < 10:
                    st.error("Failed to generate all questions. Please refresh to try again.")
                    return
                st.rerun()

        if not st.session_state.questions:
            st.error("No questions available. Please refresh the page.")
            return

        if 'quiz_completed' not in st.session_state:
            st.session_state.quiz_completed = False

        if not st.session_state.quiz_completed:
            current_q_idx = st.session_state.current_question
            question, options, correct_answer = st.session_state.questions[current_q_idx]

            st.markdown(f"### Question {current_q_idx + 1} of 10")
            st.markdown(f"<div class='question-text'>{question}</div>", unsafe_allow_html=True)
            
            # Get the previously selected answer for this question, if any
            previous_answer = st.session_state.user_answers.get(current_q_idx)
            
            user_answer = st.radio(
                "Select your answer:",
                list(options.keys()),
                format_func=lambda x: f"{x}) {options[x]}",
                index=list(options.keys()).index(previous_answer) if previous_answer else None,
                key=f"question_{current_q_idx}"
            )

            col1, col2, col3 = st.columns([2,2,1])
            
            with col1:
                if st.button("Back", disabled=(current_q_idx == 0)):
                    st.session_state.current_question -= 1
                    st.rerun()
            
            with col2:
                if st.button("Next" if current_q_idx < 9 else "Finish Quiz"):
                    if user_answer is not None:
                        st.session_state.user_answers[current_q_idx] = user_answer
                        
                        if current_q_idx < 9:
                            st.session_state.current_question += 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
                    else:
                        st.warning("Please select an answer before proceeding.")

        else:
            score = sum(1 for i, (_, _, correct_answer) in enumerate(st.session_state.questions)
                        if st.session_state.user_answers.get(i) == correct_answer)
            percentage = (score / 10) * 100

            st.markdown("## Quiz Results")
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="score-title">Your Final Score</div>
                    <div class="score-value">{score}/10</div>
                    <div class="score-percentage">({percentage:.1f}%)</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            for i, (question, options, correct_answer) in enumerate(st.session_state.questions):
                user_answer = st.session_state.user_answers.get(i)
                is_correct = user_answer == correct_answer
                
                st.markdown(f"### Question {i + 1}")
                st.markdown(f"<div class='question-text'>{question}</div>", unsafe_allow_html=True)
                st.markdown(f"Your answer: **{user_answer}) {options[user_answer]}**")
                st.markdown(f"Correct answer: **{correct_answer}) {options[correct_answer]}**")
                st.markdown(
                    f"<span class='{'correct' if is_correct else 'incorrect'}'>"
                    f"{'✓ Correct' if is_correct else '✗ Incorrect'}</span>",
                    unsafe_allow_html=True
                )
                st.markdown("---")
            
            if st.button("Start New Quiz"):
                for key in ['questions', 'current_question', 'user_answers', 'quiz_completed', 'quiz_started', 'selected_topic', 'selected_difficulty']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def main():
    try:
        set_page_config()
        quiz_interface()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        
    # Footer
    st.markdown("""
    <div class='footer'>
    Developed by <a href='https://aicraftalchemy.github.io'>Ai Craft Alchemy</a><br>
     Connect with us: <a href='tel:+917661081043'>+91 7661081043</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
