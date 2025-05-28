import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.2,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template("""
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website or a job description.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills`, `description`, and `company`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
        """)
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def extract_resume_info(self, resume_text):
        prompt_resume = PromptTemplate.from_template("""
            ### RESUME TEXT:
            {resume_text}
            ### INSTRUCTION:
            Extract the following information from the resume and return in JSON format:
            - `name`: Full name of the candidate
            - `email`: Email address
            - `phone`: Phone number (if available)
            - `skills`: List of technical skills, programming languages, frameworks, tools
            - `experience`: List of work experiences with company, role, duration, and key achievements
            - `projects`: List of personal/professional projects with descriptions
            - `education`: Educational background
            - `summary`: Brief professional summary or objective
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
        """)
        chain_resume = prompt_resume | self.llm
        res = chain_resume.invoke(input={"resume_text": resume_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Unable to parse resume information.")
        return res

    def write_candidate_email(self, job, resume_info, relevant_projects):
        prompt_email = PromptTemplate.from_template("""
            ### JOB DESCRIPTION:
            {job_description}

            ### CANDIDATE INFORMATION:
            {resume_info}

            ### RELEVANT PROJECTS:
            {relevant_projects}

            ### INSTRUCTION:
            Write a professional cold email from the candidate to apply for the job described above.

            The email must include:
            - The candidate’s full name 
            - A brief mention of their **educational background**
            - **current role or most recent activity**
            - A clear expression of **interest in the specific role and company**
            - Highlight of **key skills, technical experiences, or internships**
            - **2-3 projects** that best demonstrate relevant expertise (mention links if available)
            - A polite and enthusiastic **call-to-action**
            - A professional **closing signature with name, email, phone number**

            ### STRUCTURE:
            1. Greeting 
            2. Intro: Name , brief education background 
            3. current role or recent activity,
            4. Paragraph highlighting motivation and interest in the role
            5. Paragraph summarizing top relevant experiences and technical skills
            6. Paragraph showcasing 2-3 relevant projects with links (if any)
            7. Closing: Appreciation, enthusiasm, and request for next steps
            8. Signature: Full name, email, and phone number

            Keep the tone warm, confident, and professional. Word count: 200–300 words.

            ### EMAIL (NO PREAMBLE):
        """)
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job),
            "resume_info": str(resume_info),
            "relevant_projects": str(relevant_projects)
        })
        return res.content

    def parse_job_description(self, job_text):
        prompt_parse = PromptTemplate.from_template("""
            ### JOB DESCRIPTION TEXT:
            {job_text}
            ### INSTRUCTION:
            Parse this job description and return in JSON format containing the following keys: 
            `role`, `company`, `experience`, `skills`, `description`, `location` (if mentioned).
            Extract the key requirements and responsibilities.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
        """)
        chain_parse = prompt_parse | self.llm
        res = chain_parse.invoke(input={"job_text": job_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Unable to parse job description.")
        return res

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
