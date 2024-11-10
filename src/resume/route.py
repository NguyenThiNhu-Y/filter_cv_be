import os
import sys
from fastapi import APIRouter, UploadFile, HTTPException, status

from resume.request import (
    CrawlResumeRequest, 
    SearchResume, 
)
from resume.service import crawl_resume, find_folder_of_resume, save_resume
from utils import calculate_hash, validate_file
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

sys.path.append(".")

router = APIRouter()

@router.post("/search")
def get_all(search_request: SearchResume):
    resumes = resume_mongodb.get_all_resume_by_folder_id(search_request.folder_id, search_request.page, search_request.limit)
    return resumes

@router.post("/crawl_resume")
def crawl(crawl_resume_request: CrawlResumeRequest):
    crawl_resume(crawl_resume_request.user_id, crawl_resume_request.start_date, crawl_resume_request.end_date)

@router.post("/find_folder_of_resume")
def find_folder():
    rs = find_folder_of_resume("66f94d7b902134342552db57", r"CVs\66f94d7b902134342552db57\CV_AI_Engineer.pdf")
    return rs

@router.post("/upload")
async def upload_resume(resume: UploadFile, folder_id: str):
    isValid, error = validate_file(resume)

    if not isValid:
        raise error

    resume_bytes = await resume.read()
    resume_hash = calculate_hash(resume_bytes)
    duplicated_resume = resume_mongodb.find_resume_by_hash(resume_hash, folder_id)

    if duplicated_resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file already exists",
        )
    # save file to folder
    folder_path = f"CVs\{folder_id}"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, resume.filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(resume_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save the file: {str(e)}")
    
    resume_id = save_resume(folder_id, file_path, resume_hash)
    return resume_id
    
    