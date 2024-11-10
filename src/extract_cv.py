import os
import sys
import fitz
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

from resume.request import ResumeData

sys.path.append(".")
from config import cfg

load_dotenv()
cfg_prompt = cfg.prompt
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

def extract_text_from_page(page):
   text_page = ""
   for text in page.get_text("blocks"):
      if text[4].replace("\n", "").strip() != "":
         text_page += text[4].replace("\n", "").strip() + "\n"
   return text_page

def extract_text_from_pdf(file_path):
   file_name = os.path.basename(file_path)
   doc = fitz.open(file_path)
   doc_text = ""
   for page in doc:
      page_text = extract_text_from_page(page)
      doc_text += page_text
   with open(os.path.join('extract_files', file_name.replace(".pdf", ".txt")), 'w', encoding='utf-8') as file:
      file.write(doc_text)
   return doc_text

# def extract_content_cv(file_path):
#    file_path = r"CVs\CV_AI_Engineer.pdf"
#    doc = fitz.open(file_path)

#    content = ""
#    for page in doc:
#       content+=page.get_text()

#    with open(r'extract_files\CV_AI_Engineer.txt', 'w', encoding='utf-8') as file:
#       file.write(content)

   # return content

def extract_criteria(content_cv):
   # model = ChatOpenAI(
   #             model='gpt-4', 
   #             openai_api_key=OPENAI_API_KEY,
   #             temperature=1
   #          )
   # prompt_extract = cfg_prompt["prompt"].format(content_cv=content_cv, resume_template=cfg_prompt["resume_template"])
   # prompt = [HumanMessage(
   #              content=prompt_extract
   #          )]
   # response = model.generate(
   #                      [prompt]
   #                   )
   # response = response.generations[0][0].text.replace('```json','').replace('```', '').strip()
   response = """
{
    "basicInfo": {
        "fullName": "Nguyen Thi Nhu Y",
        "email": "nhuyhe62001@gmail.com",
        "phoneNumber":"+84 327 048 268",
        "address": null,
        "linkedInMainPageUrl": null,
        "githubMainPageUrl": "https://github.com/NguyenThiNhu-Y",
        "portfolioMainPageUrl": null,
        "jobTitle": "AI Engineer",
        "summaryOrObjectives": "I look forward to working in a professional programming environment, where I can develop professional"   
    },
    "skills": ["Chatbot Development","Image Processing","Image Detection","Large Language Models (LLM)",
                "Embedding Techniques","Optical Character Recognition (OCR)","Python","Java","C#","HTML",
                "CSS","Javascript","Git","Postman","Figma","StarUML","SQL Server","PostgreSQL","MySQL","Docker",
                ".NET", "Laravel"],
    "languages": null,
    "awards": null,
    "certifications": null,
    "educations": [{
        "educationName": "Information Technology",
        "startDate": null,
        "endDate": null,
        "major": "Information Technology",
        "gpa": 3.84
    }],
    "workExperiences": [{
            "companyName": "FPT Software",
            "jobTitle": "AI Engineer",
            "jobSumary": "Worked on Document Processing, Chatbot Development, OCR, Image Detection and Noise Reduction",
            "startDate": "2023-01-01",
            "endDate": null
        }, {
            "companyName": "Freelancer",
            "jobTitle": "Chatbot Developer",
            "jobSumary": "Worked on Chatbot Development, Document Processing",
            "startDate": "2024-03-01",
            "endDate": "2024-07-31"
        }, {
            "companyName": "FindX Corp",
            "jobTitle": "Backend Developer",
            "jobSumary": "Responsible for Backend development for 3 HR management modules",
            "startDate": "2022-03-01",
            "endDate": "2023-03-01"
        }],
    "projectExperiences": null
}
"""
   response_json = ResumeData.model_validate_json(response)
   print(response_json)
   with open(r'extract_files\extract_criteria.txt', 'w', encoding='utf-8') as file:
      file.write(response)
   return response_json

# files = os.listdir("CVs")
# for file in files:
#    file_path = os.path.join("CVs", file)
#    extract_text_from_pdf(file_path)

# with open(r'extract_files\CV_Nguyen_Thi_Nhu_Y_Intern_NET-1.txt', 'r', encoding='utf-8') as file:
#    content = file.read()
# extract_criteria(content)

# import json
# with open(r'extract_files\extract_criteria.txt', 'r', encoding='utf-8') as file:
#    content = file.read()
# data = json.loads(content)
# print(data)
