import logging
from uuid import uuid4
from fastapi import FastAPI, Request, UploadFile, File, Depends, status, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from pydantic import Field

from src.core import get_db_session, async_engine
from src.models import Base
from src.services import ResumeService, ResumeParsingError, ResumeNotFoundError, JobService, JobNotFoundError
from src.schemas.pydantic.job import JobUploadRequest

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post(
    "/upload_resume",
    summary="Upload a resume in only PDF format and store it into DB in HTML/Markdown format",
)
async def upload_resume(
        request: Request,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db_session),
):
    """
    Accepts only PDF file, converts it to HTML/Markdown, and stores it in the database.

    Raises:
        HTTPException: If the file type is not supported or if the file is empty.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))

    allowed_content_types = [
        "application/pdf",
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are allowed.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file. Please upload a valid file.",
        )

    try:
        resume_service = ResumeService(db)
        resume_id = await resume_service.convert_and_store_resume(
            file_bytes=file_bytes
        )
    except Exception as e:
        logger.error(
            f"Error processing file: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )

    return {
        "message": f"File {file.filename} successfully processed as MD and stored in the DB",
        "request_id": request_id,
        "resume_id": resume_id,
    }


@app.get(
    "/both_resume",
    summary="Get resume data from both resume and processed_resume models",
)
async def get_resume(
        request: Request,
        resume_id: str = Query(..., description="Resume ID to fetch data for"),
        db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves resume data from both resume_model and processed_resume model by resume_id.

    Args:
        resume_id: The ID of the resume to retrieve

    Returns:
        Combined data from both resume and processed_resume models

    Raises:
        HTTPException: If the resume is not found or if there's an error fetching data.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    headers = {"X-Request-ID": request_id}

    try:
        if not resume_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="resume_id is required",
            )

        resume_service = ResumeService(db)
        resume_data = await resume_service.get_resume_with_processed_data(
            resume_id=resume_id
        )

        if not resume_data:
            raise ResumeNotFoundError(
                message=f"Resume with id {resume_id} not found"
            )
        print(resume_data)

        return JSONResponse(
            content={
                "request_id": request_id,
                "data": resume_data,
            },
            headers=headers,
        )

    except ResumeNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error fetching resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching resume data",
        )


@app.post(
    "/upload_job",
    summary="stores the job posting in the database by parsing the JD into a structured format JSON",
)
async def upload_job(
        payload: str,
        request: Request,
        db: AsyncSession = Depends(get_db_session),
):
    """
    Accepts a job description as a MarkDown text and stores it in the database.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))

    # allowed_content_types = [
    #     "application/json",
    # ]
    #
    # content_type = request.headers.get("content-type")
    # if not content_type:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Content-Type header is missing",
    #     )
    #
    # if content_type not in allowed_content_types:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Invalid Content-Type. Only {', '.join(allowed_content_types)} is/are allowed.",
    #     )

    try:
        job_service = JobService(db)
        job_id = await job_service.convert_and_store_job(payload)
    except AssertionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )

    return {
        "message": "data successfully processed",
        "job_id": job_id,
        "request": {
            "request_id": request_id,
            "payload": payload,
        },
    }


@app.get(
    "/both_job",
    summary="Get job data from both job and processed_job models",
)
async def get_job(
        request: Request,
        job_id: str = Query(..., description="Job ID to fetch data for"),
        db: AsyncSession = Depends(get_db_session),
):
    """
    Retrieves job data from both job_model and processed_job model by job_id.

    Args:
        job_id: The ID of the job to retrieve

    Returns:
        Combined data from both job and processed_job models

    Raises:
        HTTPException: If the job is not found or if there's an error fetching data.
    """
    request_id = getattr(request.state, "request_id", str(uuid4()))
    headers = {"X-Request-ID": request_id}

    try:
        if not job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_id is required",
            )

        job_service = JobService(db)
        job_data = await job_service.get_job_with_processed_data(
            job_id=job_id
        )

        if not job_data:
            raise JobNotFoundError(
                message=f"Job with id {job_id} not found"
            )

        return JSONResponse(
            content={
                "request_id": request_id,
                "data": job_data,
            },
            headers=headers,
        )

    except JobNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error fetching job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching job data",
        )
