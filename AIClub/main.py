import streamlit as st
from PyPDF2 import PdfReader

import openai
import os
from dotenv import load_dotenv
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(file):
    reader= PdfReader(file)
    text=""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content 
    return text

def get_questions(text , num_questions=5):
    prompt= f"""
            Act as a teacher and create a {num_questions} multiple-choice questions (MCQ) based on the text delimted by four backquotes, the response must be formatted in JSON. Each question contains id, question, options as list, correct_answer.
            
            The text is: ''''{text}''''

            """
    response = openai.ChatCompletion.create(
        model= "gpt-3.5-turbo-16k",
        messages=[
            {
                "role": "system",
                "content" : prompt,
            },
        ],
    )
    return json.loads(response["choices"][0]["message"]["content"])
def display_questions(questions):
    for question in questions:
        question_id = str(question["id"])
        st.write(
            f"## Q{question_id}\ {question['question']}",
        )

        option_text=""
        options= question["options"]
        for option in options:
            option_text += f"- {option}\n"
        st.write(option_text)
        with st.expander("show answer", expanded=False):
            st.write(question["correct_answer"])
        st.divider()
    st.subheader("End of questions")




def main():
    st.set_page_config(page_title="Quizlet app", page_icon="❤️")
    st.title("Quizlet app")
    st.write(" this is a simple quizlet app by Aysha Aljaafari.")
    st.divider()

    with st.form(key="upload_file"):
        upload_file = st.file_uploader("Upload a PDF file" , type=["pdf", "txt"])

        number_of_questions = st.number_input(
            "How many question do you want me to generate? *note: minimum 2 questions", min_value=2, max_value=10 , value=5
        )
        submit_button = st.form_submit_button(
            label="Generate Questions", type="primary"
        )

    if submit_button:
        if upload_file:
            text= extract_text_from_pdf(upload_file)
            with st.spinner("Generating questions..."):
                questions= get_questions(text, number_of_questions)["questions"]
            #st.write(questions)
            display_questions(questions)
        else:
            st.error("please upload a PDF file.")

if __name__ == "__main__":
    main()