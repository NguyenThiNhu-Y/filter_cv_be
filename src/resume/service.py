import os
import re
import sys
import fitz
import json
import base64
from PIL import Image
import io
import numpy as np
import ast

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.schema import HumanMessage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from utils import calculate_hash_by_file_path
from sentence_transformers import util

sys.path.append(".")
from config import cfg
from database.folder import Folder
from resume.request import (
   AwardRequest, 
   CertificationRequest,
   EducationRequest, 
   LanguageRequest, 
   ProjectExperienceRequest, 
   ReferencesRequest,
   ResumeData, 
   ResumeRequest,
   SearchResume,
   SkilRequest, 
   WorkExperienceRequest
)
from database.resume import Resume as ResumeMongoDB
from database.resume_reference import ResumeReference as ResumeReferenceMongoDB
from database.resume_award import ResumeAward as ResumeAwardMongoDB
from database.resume_education import ResumeEducation as ResumeEducationMongoDB
from database.resume_certificate import ResumeCertificate as ResumeCertificateMongoDB
from database.resume_language import ResumeLanguage as ResumeLanguageMongoDB
from database.resume_project_experience import ResumeProjectExperience as ResumeProjectExperienceMongoDB
from database.resume_work_experience import ResumeWorkExperience as ResumeWorkExperienceMongoDB
from database.resume_skill import ResumeSkill as ResumeSkillMongoDB

resume_mongodb = ResumeMongoDB()
resume_reference_mongodb = ResumeReferenceMongoDB()
resume_award_mongodb = ResumeAwardMongoDB()
resume_education_mongodb = ResumeEducationMongoDB()
resume_certificate_mongodb = ResumeCertificateMongoDB()
resume_language_mongodb = ResumeLanguageMongoDB()
resume_project_experience_mongodb = ResumeProjectExperienceMongoDB()
resume_work_experience_mongodb = ResumeWorkExperienceMongoDB()
resume_skill_mongodb = ResumeSkillMongoDB()


load_dotenv()
cfg_prompt = cfg.prompt
cfg_file = cfg.file
folder_db = Folder()
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

def extract_text_from_page(page):
   text_page = ""
   for text in page.get_text("blocks"):
      if text[4].replace("\n", "").strip() != "":
         text_page += text[4].replace("\n", "").strip() + "\n"
   return text_page

def extract_text_from_pdf(file_path):
   doc = fitz.open(file_path)
   doc_text = ""
   for page in doc:
      page_text = extract_text_from_page(page)
      doc_text += page_text
   return doc_text

def extract_criteria(content_cv):
   model = ChatOpenAI(
               model='gpt-4', 
               openai_api_key=OPENAI_API_KEY,
               temperature=1
               )
   prompt_extract = cfg_prompt["prompt"].format(content_cv=content_cv, resume_template=cfg_prompt["resume_template"])
   prompt = [HumanMessage(
                  content=prompt_extract
               )]
   response = model.generate(
                           [prompt]
                     )
   response = response.generations[0][0].text.replace('```json','').replace('```', '').strip()
   
   response_json = ResumeData.model_validate_json(response)
   return response_json

def generate_thumbnails(pdf_path):
   doc = fitz.open(pdf_path)
   page = doc.load_page(0)
   pix = page.get_pixmap()
   img = Image.open(io.BytesIO(pix.tobytes("png")))
   img_byte_arr = io.BytesIO()
   img.save(img_byte_arr, format='PNG')
   img_byte_arr.seek(0)
   img_base64 = base64.b64encode(img_byte_arr.read()).decode('utf-8')
   doc.close()
   return img_base64

def embedding(text: str):
   model = OpenAIEmbeddings(
      model="text-embedding-3-large",
   )
   embedding = []
   if text:
      embedding = model.embed_query(text)
   return embedding

def crawl_resume(user_id, start_date, end_date):
   creds = None
   # Kiểm tra token xác thực
   if os.path.exists(cfg_file["token_file_path"]):
      with open(cfg_file["token_file_path"], 'r') as token:
         creds = json.load(token)

   # Nếu chưa có token hoặc token hết hạn, tiến hành xác thực
   if not creds or not creds.get('valid'):
      flow = InstalledAppFlow.from_client_secrets_file(cfg_file["credential_file_path"], cfg_file["scopes"])
      creds = flow.run_local_server(port=0)
      # Lưu token
      with open(cfg_file["token_file_path"], 'w') as token:
         token.write(creds.to_json())  # Chuyển đổi creds thành JSON

   # Kết nối tới Gmail API
   service = build('gmail', 'v1', credentials=creds)

   # Lấy email có đính kèm CV trong khoảng thời gian
   query = 'has:attachment CV'
   if start_date:
      query += f' after:{start_date}'
   if end_date:
      query += f' before:{end_date}'
   results = service.users().messages().list(userId='me', q=query).execute()
   messages = results.get('messages', [])

   list_resume_id = []
   if not messages:
      print("No messages found.")
   else:
      for message in messages:
         msg = service.users().messages().get(userId='me', id=message['id']).execute()
         for part in msg['payload']['parts']:
            if part['filename']:
               print(f"Found attachment: {part['filename']}")

               # Tải tệp đính kèm
               attachment_id = part['body']['attachmentId']
               attachment = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=attachment_id).execute()
               data = attachment['data']
               file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

               # Lưu tệp đính kèm
               folder_cvs_path = os.path.join(cfg_file["folder_cvs_path"], user_id)
               os.makedirs(folder_cvs_path, exist_ok=True)
               path = os.path.join(folder_cvs_path, part['filename'])
               with open(path, 'wb') as f:
                  f.write(file_data)

               # lấy folder id tương ứng, để lưU
               folder_id = find_folder_of_resume(user_id, path)
               resume_id = save_resume(folder_id, path)
               list_resume_id.append(resume_id)
   return list_resume_id

def find_folder_of_resume(user_id, file_path):
   file_name = os.path.basename(file_path)
   resume_content = extract_text_from_pdf(file_path)
   list_folder = folder_db.get_all_folder_by_user_id(user_id, 1, 9999, "")
   model = ChatOpenAI(
               model='gpt-4', 
               openai_api_key=OPENAI_API_KEY,
               temperature=1
            )
   prompt_extract = cfg_prompt["find_folder"].format(file_name=file_name, content_cv=resume_content, list_folder=list_folder)
   prompt = [HumanMessage(
                content=prompt_extract
            )]
   response = model.generate(
                        [prompt]
                     )
   response = response.generations[0][0].text.replace('```json','').replace('```', '').strip()

   pattern = r'\"[0-9a-fA-F]{24}\"'
   folder_id = re.findall(pattern, response)

   try:
      folder_id = [oid.strip('"') for oid in folder_id][0]
   except Exception as e:
      folder_id = ""
   return folder_id

def save_resume(folder_id, file_path, resume_hash=""):
   if resume_hash == "":
      resume_hash = calculate_hash_by_file_path(file_path)
   # parse and save resume data
   resume_content = extract_text_from_pdf(file_path)
   resume_data = extract_criteria(resume_content)

   # process thumbnail
   thumbnail_base64 = generate_thumbnails(file_path)

   # save resume
   resume_request = ResumeRequest(
      resume_file_hash=resume_hash,
      resume_file_path=file_path,
      resume_thumbnail_base64=thumbnail_base64,
      folder_id=folder_id,
      job_title=resume_data.basicInfo.jobTitle,
      job_title_embedding=embedding(resume_data.basicInfo.jobTitle),
      summary_or_objectives=resume_data.basicInfo.summaryOrObjectives,
      full_name=resume_data.basicInfo.fullName,
      email=resume_data.basicInfo.email,
      phone_number=resume_data.basicInfo.phoneNumber,
      address=resume_data.basicInfo.address,
      tolal_years_experience=0,
   )
   resume_id = resume_mongodb.create_resume(resume_request)

   # save reference
   if resume_data.basicInfo.linkedInMainPageUrl:
      reference_request = ReferencesRequest(
         resume_id=resume_id,
         reference_link=resume_data.basicInfo.linkedInMainPageUrl,
      )
      resume_reference_mongodb.create_resume_reference(reference_request)

   if resume_data.basicInfo.githubMainPageUrl:
      reference_request = ReferencesRequest(
         resume_id=resume_id, reference_link=resume_data.basicInfo.githubMainPageUrl
      )
      resume_reference_mongodb.create_resume_reference(reference_request)

   if resume_data.basicInfo.portfolioMainPageUrl:
      reference_request = ReferencesRequest(
         resume_id=resume_id,
         reference_link=resume_data.basicInfo.portfolioMainPageUrl,
      )
      resume_reference_mongodb.create_resume_reference(reference_request)

   # save award
   if resume_data.awards:
      for item in resume_data.awards:
         award_request = AwardRequest(
               resume_id=resume_id,
               title=item.title,
               award_title_embedding=embedding(item.title),
               date=item.date,
         )
         resume_award_mongodb.create_resume_award(award_request)

   # save certifications
   if resume_data.certifications:
      for item in resume_data.certifications:
         certification_request = CertificationRequest(
               resume_id=resume_id,
               title=item.title,
               certification_embedding=embedding(item.title),
               date=item.date,
         )
         resume_certificate_mongodb.create_resume_certificate(certification_request)

   # save educations
   if resume_data.educations:
      for item in resume_data.educations:
         education_request = EducationRequest(
               resume_id=resume_id,
               name=item.educationName,
               education_name_embedding=embedding(item.educationName),
               start_date=item.startDate,
               end_date=item.endDate,
               gpa=item.gpa,
               major=item.major
         )
         resume_education_mongodb.create_resume_education(education_request)

   # save workExperiences
   if resume_data.workExperiences:
      for item in resume_data.workExperiences:
         workExperiences_request = WorkExperienceRequest(
               resume_id=resume_id,
               job_title=item.jobTitle,
               job_summary=item.jobSumary,
               company_name=item.companyName,
               start_date=item.startDate,
               end_date=item.endDate,
         )
      resume_work_experience_mongodb.create_resume_work_experience(workExperiences_request)

   # save language
   if resume_data.languages:
      for item in resume_data.languages:
         language_request = LanguageRequest(
               resume_id=resume_id,
               language_name=item,
               language_name_embedding=embedding(item),
         )
         resume_language_mongodb.create_resume_language(language_request)

   # save project experience
   if resume_data.projectExperiences:
      for item in resume_data.projectExperiences:
         projectExperiences_request = ProjectExperienceRequest(
               resume_id=resume_id,
               project_name=item.projectName,
               project_description=item.description,
               project_technologies=item.technologies,
               responsibilities=item.responsibilities,
               repository_url=item.repositoryUrl,
               demo_or_live_url=item.demoOrLiveUrl,
               start_date=item.startDate,
               end_date=item.endDate,
         )
         resume_project_experience_mongodb.create_resume_project_experience(projectExperiences_request)

   # save skill
   if resume_data.skills:
      for item in resume_data.skills:
         skill_request = SkilRequest(
               resume_id=resume_id,
               skill_name=item,
               skill_name_embedding=embedding(item),
         )
         resume_skill_mongodb.create_resume_skill(skill_request)

   return resume_id

def get_award(resume_id):
   award = resume_award_mongodb.get_resume_award_by_resume_id(resume_id)
   award_title_embedding = [item['award_title_embedding'] for item in award]
   return award_title_embedding

def get_certificate(resume_id):
   certificate = resume_certificate_mongodb.get_resume_certificate_by_resume_id(resume_id)
   certification_embedding = [item['certification_embedding'] for item in certificate]
   return certification_embedding

def get_education(resume_id):
   education = resume_education_mongodb.get_resume_education_by_resume_id(resume_id)
   education_name_embedding = [item['education_name_embedding'] for item in education]
   return education_name_embedding

def get_language(resume_id):
   language = resume_language_mongodb.get_resume_language_by_resume_id(resume_id)
   language_name_embedding = [item['language_name_embedding'] for item in language]
   return language_name_embedding

def get_skill(resume_id):
   skill = resume_skill_mongodb.get_resume_skill_by_resume_id(resume_id)
   skill_name_embedding = [item['skill_name_embedding'] for item in skill]
   return skill_name_embedding

def search_resume(request_search: SearchResume):
   result_resume_search = []
   if not request_search.folder_id:
        return []

   resumes = resume_mongodb.get_all_resume_by_folder_id(request_search.folder_id, 1, 99999)

   query_embedding_job_title = embedding(request_search.job_title)
   results = []
   for resume in resumes:
      # job_title_embedding = resume['job_title_embedding']
      # similarity = np.dot(query_embedding_job_title, job_title_embedding) / (
      #    np.linalg.norm(query_embedding_job_title) * np.linalg.norm(job_title_embedding)
      # )
      # results.append({"resume": resume, "similarity": similarity})

      resume_id = resume["resume_id"]
      award_title_embedding = get_award(resume_id)

      certification_embedding = get_certificate(resume_id)

      education_name_embedding = get_education(resume_id)

      language_name_embedding = get_language(resume_id)

      skill_name_embedding =get_skill(resume_id)

      search_awards = True
      for award in request_search.awards:
         query_embedding_award = embedding(award.value)
         select_awards = util.semantic_search(
            np.array(query_embedding_award, dtype=np.float32),
            np.array(award_title_embedding, dtype=np.float32),
         )[0]
         select_awards = [item for item in select_awards if item["score"] >= 0.76]
         if len(select_awards) == 0 and award.required:
            search_awards = False
            break

      search_certifications = True
      for certification in request_search.certificates:
         query_embedding_certification = embedding(certification.value)
         select_certifications = util.semantic_search(
               np.array(query_embedding_certification, dtype=np.float32),
               np.array(certification_embedding, dtype=np.float32),
         )[0]
         select_certifications = [
               item for item in select_certifications if item["score"] >= 0.76
         ]
         if len(select_certifications) == 0 and certification.required:
               search_certifications = False
               break

      search_languages = True
      for language in request_search.languages:
         query_embedding_language = embedding(language.value)
         select_languages = util.semantic_search(
               np.array(query_embedding_language, dtype=np.float32),
               np.array(language_name_embedding, dtype=np.float32),
         )[0]
         select_languages = [
               item for item in select_languages if item["score"] >= 0.76
         ]
         if len(select_languages) == 0 and language.required:
               search_languages = False
               break

      search_educations = True
      for education in request_search.educations:
         query_embedding_education = embedding(education.value)
         select_educations = util.semantic_search(
               np.array(query_embedding_education, dtype=np.float32),
               np.array(education_name_embedding, dtype=np.float32),
         )[0]
         select_educations = [
               item for item in select_educations if item["score"] >= 0.76
         ]
         if len(select_educations) == 0 and education.required:
               search_educations = False
               break

      search_skills = True
      for skill in request_search.skills:
         query_embedding_skill = embedding(skill.value)
         select_skills = util.semantic_search(
               np.array(query_embedding_skill, dtype=np.float32),
               np.array(skill_name_embedding, dtype=np.float32),
         )[0]
         print("select_skills", select_skills)
         select_skills = [item for item in select_skills if item["score"] >= 0.76]
         if len(select_skills) == 0 and skill.required:
               search_skills = False
               break

      if (
         search_awards
         and search_certifications
         and search_languages
         and search_educations
         and search_skills
      ):
         result_resume_search.append(resume)

   return result_resume_search

