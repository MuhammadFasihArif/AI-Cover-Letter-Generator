import os
import pandas as pd
import random
import textwrap
import streamlit as st
from groq import Groq
from project_scrape_jobs import ScrapeJobs
from project_scrape_link import Scraping_Links
from connection import Database


class AICoverLetterGenerator:
    def __init__(self, api_key, csv_file='upwork_job.csv', db_config=None):
        self.client = Groq(api_key=api_key)
        self.csv_file = csv_file
        self.db = Database(**db_config)  # Initialize Database with db_config

    def load_job_data(self):
        if os.path.exists(self.csv_file):
            return pd.read_csv(self.csv_file, encoding='ISO-8859-1')  # Specify encoding here
        return pd.DataFrame()


    def display_job_titles(self, df):
        job_titles_list = []
        for index, row in df.iterrows():
            job_titles_list.append(f"{index}: {row['Job Title']}")
        return "\n".join(job_titles_list)

    def to_markdown(self, text):
        text = text.replace('•', '  *')
        return st.markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

    def random_style(self):
        styles = [
            "formal and professional",
            "casual and conversational",
            "creative and narrative",
            "straightforward and concise",
            "persuasive and impactful",
            "warm and friendly",
            "assertive and confident",
            "enthusiastic and energetic",
            "detailed and descriptive",
            "minimalistic and to the point"
        ]
        return random.choice(styles)

    def extract_style(self, prompt):
        styles = [
            "formal and professional",
            "casual and conversational",
            "creative and narrative",
            "straightforward and concise",
            "persuasive and impactful",
            "warm and friendly",
            "assertive and confident",
            "enthusiastic and energetic",
            "detailed and descriptive",
            "minimalistic and to the point"
        ]
        for style in styles:
            if style in prompt.lower():
                return style
        return None

    def save_cover_letter_to_db(self, letter):
        try:
            self.db.insertion_in_proposal(letter)
        except Exception as e:
            print(f"Error inserting into database: {e}")

    def save_relevancy_to_db(self,relevancy):
        try:
            self.db.insert_relevancy(relevancy)
        except Exception as e:
            print(f"Error inserting to databse:{e}")

    def generate_response(self, prompt):
        df = self.load_job_data()
        specified_style = self.extract_style(prompt)
        selected_style = specified_style if specified_style else self.random_style()

        if "scrape" in prompt.lower():
            zenrows_apikey = '7cb7c5c87bad0d532d8dc4400305615f17535329'
            ScrapeJobs.scrape_upwork_job_data(zenrows_apikey)
            return "Job data scraped and saved."

        elif "show" in prompt.lower() and "jobs" in prompt.lower():
            if not df.empty:
                job_titles_text = self.display_job_titles(df)
                return f"Available jobs:\n{job_titles_text}"
            else:
                return "No job data available. Please scrape job data first."
        if ("relevance" in prompt.lower() or "relevancy" in prompt.lower() or "relevant" in prompt.lower()) and "job" in prompt.lower():
                    job_number_str = ''.join(filter(str.isdigit, prompt))
                    if job_number_str.isdigit():
                        job_number = int(job_number_str)
                        if 0 <= job_number < len(df):
                            job_description = df.loc[job_number, 'Job Description']
                            job_title = df.loc[job_number, 'Job Title']

                            # Construct the prompt for LLaMA API
                            llama_prompt = f"Please assess the relevance of the following job description to the data engineering domain: \n\nJob Title: {job_title}\n\nJob Description: {job_description}\n\nProvide a relevance score from 1 to 10."

                            # Send the prompt to the LLaMA API
                            completion = self.client.chat.completions.create(
                                model="llama3-70b-8192",
                                messages=[
                                    {"role": "system", "content": "You are an expert in job description analysis."},
                                    {"role": "user", "content": llama_prompt}
                                ],
                                temperature=0.5,
                                max_tokens=1024,
                                top_p=1,
                                stream=False,
                                stop=None,
                            )

                            # Correctly access the content of the response
                            response_text = completion.choices[0].message.content.strip()
                            self.save_relevancy_to_db(response_text)
                            return f"Job {job_number}: {job_title} - Relevance Score: {response_text}"

                        else:
                            return "Invalid job number. Please enter a valid number from the CSV file."
                    else:
                        return "Please enter a valid job number."

        if "show relevant jobs" in prompt.lower():
            relevant_jobs = []
            job_indexes = []

            for index, row in df.iterrows():
                job_description = row['Job Description']
                job_title = row['Job Title']

                # Construct the prompt for LLaMA API
                llama_prompt = f"Please assess the relevance of the following job description to the data engineering domain: \n\nJob Title: {job_title}\n\nJob Description: {job_description}\n\nProvide a relevance score from 1 to 10."

                # Send the prompt to the LLaMA API
                completion = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are an expert in job description analysis."},
                        {"role": "user", "content": llama_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=50,
                    top_p=1,
                    stream=False,
                    stop=None,
                )

                # Get the relevance score
                relevance_score = float(completion.choices[0].message.content.strip())

                # Check if the job is relevant (score above 8)
                if relevance_score > 8:
                    relevant_jobs.append(f"Job {index}: {job_title} - Relevance Score: {relevance_score}")
                    job_indexes.append(index)  # Keep track of indexes

            if relevant_jobs:
                return "Relevant jobs related to Data Engineering (Relevance Score > 8):\n\n" + "\n".join(relevant_jobs)
            else:
                return "No jobs found with a relevance score above 8 related to Data Engineering."




        elif "job" in prompt.lower() and ("Coverletter" in prompt.lower() or "proposal" in prompt.lower() or "cover letter" in prompt.lower()):
            job_number_str = ''.join(filter(str.isdigit, prompt))
            if job_number_str.isdigit():
                job_number = int(job_number_str)
                if 0 <= job_number < len(df):
                    job_title = df.loc[job_number, 'Job Title'].replace('*', '').replace('/', '_').replace('\\', '_')
                    job_description = df.loc[job_number, 'Job Description']
                    skills = df.loc[job_number, 'Required Skills']

                    base_prompt = f"Write a {selected_style} cover letter for the job title '{job_title}' with the following description: '{job_description}' and include the following job skills in bullet points: '{skills}'"

                    if "remove bullets" in prompt.lower():
                        base_prompt = base_prompt.replace("in bullet points", "without bullet points")
                    elif "insert bullets" in prompt.lower():
                        base_prompt = base_prompt.replace("in bullet points", "in bullet points")

                    completion = self.client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": "You are an excellent cover letter writer"},
                            {"role": "user", "content": base_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1024,
                        top_p=1,
                        stream=True,
                        stop=None,
                    )

                    response_text = "".join([chunk.choices[0].delta.content or "" for chunk in completion])
                    self.save_cover_letter_to_db(response_text)
                    return response_text  # Return the plain text instead of calling st.markdown() here

                else:
                    return "Invalid job number. Please enter a valid number from the CSV file."
            else:
                return "Please enter a valid job number."

        else:
            completion = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are an excellent assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

            response_text = "".join([chunk.choices[0].delta.content or "" for chunk in completion])
            return response_text  # Return the plain text instead of calling st.markdown() here
    def show_welcome_screen(self):
        st.title("Welcome to AI Cover Letter Generator")
        st.write("Please log in to continue.")
        if st.button("Login"):
            st.session_state["logged_in"] = True
            st.experimental_rerun()


    def run_app(self):
        

        st.sidebar.header("Job Extraction")
        domain_input = st.sidebar.text_input("Enter domain for job extraction:", "")
        extract_button = st.sidebar.button("Extract Job Links")
        logOut_button = st.sidebar.button("Logout")

        if extract_button and domain_input:
            Scraping_Links.scrape_job_links(domain_input)
            st.sidebar.success(f"Job links extracted for domain: {domain_input}")

        if logOut_button:
            st.session_state["logged_in"] = False
            st.session_state["page"] = "welcome"
            st.rerun(scope="app")


        col1, col2, col3 = st.columns(3)
        with col1: st.write(' ')
        with col2:
            st.image("Dotlabs Logo white.png", width=200)
            st.markdown("""
            <div style='
                text-align: center; 
                color: #FFA500; 
                padding-right: 50px;'>
                <h2 style='
                    margin: 0;color: #FFA500; '>
                    Ai <span style='white-space: nowrap;color: #FFA500; '>CoverLetter</span><br>
                    Generator
                </h2>
            </div>""", unsafe_allow_html=True)
        with col3: st.write(' ')

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({"role": "assistant", "content": "Hi! How can I assist you today?"})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter your job-related prompt here"):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                loading_animation = st.empty()
                loading_animation.markdown("⏳ Generating response...")

                try:
                    response = self.generate_response(prompt)
                    loading_animation.empty()
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response)

                except ValueError:
                    loading_animation.empty()
                    error_message = "An error occurred. Please try again."
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    st.markdown(error_message)



# Example usage:
if __name__ == "__main__":
    api_key = "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"
    db_config = {
        'db_host': 'localhost',
        'db_name': 'project',
        'db_user': 'postgres',
        'db_password': 'admin',
        'db_port': int(os.getenv('DB_PORT', 5432))
    }

    app = AICoverLetterGenerator(api_key, db_config=db_config)
    app.run_app()
