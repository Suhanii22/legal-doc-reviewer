from fastapi import APIRouter, UploadFile, File, HTTPException, status , Depends , Header
from sqlalchemy.orm import Session

from app import models, schemas
from app.db.database import get_db
from app.utils.oauth2 import get_current_user
from app.utils.pdf import extract_text
from app.utils.chunking import split_into_chunks


router = APIRouter(
    prefix="/contract",
    tags=["Contracts"]
)


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED
)
async def upload_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    idempotency_key: str = Header(...),
    current_user: models.User = Depends(get_current_user)
):

    print(models.ContractStatus)
    print(dir(models.ContractStatus))

    # # idempotency
    # existing = (
    #     db.query(models.Contract)
    #     .filter(models.Contract.idempotent_key == idempotency_key)
    #     .first()
    # )
    
    # if existing:
    #    return {
    #     "message": "Already uploaded",
    #     "contract_id": existing.id,
    #     "filename": existing.filename,
    #    }
    
    # Ensure a file was uploaded
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded."
        )

    # Allow only PDF files
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed."
        )

    # Create contract record
    contract = models.Contract(
        filename=file.filename,
        user_id=current_user.id,
        idempotent_key=idempotency_key,
        status=models.ContractStatus.Uploaded
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    # Read uploaded PDF into memory
    pdf_bytes = await file.read()

    # Extract text
    extracted_text = extract_text(pdf_bytes)

    print("Its extracted text----------------------------------------------------------------------------------------",extracted_text)

    clauses = split_into_chunks(extracted_text)

    print("its clauses",clauses)

    for index, clause_text in enumerate(clauses):

        clause = models.Clause(
            contract_id=contract.id,
            text=clause_text,
            position_in_doc=index + 1
        )
        print(
        "Clause no:",
        index + 1,
        "Text:",
        clause.text
        )
        db.add(clause)

    db.commit()


    return {
        "message": "PDF accepted successfully",
        "contract_id": contract.id,
        "filename": file.filename,
        "characters": len(extracted_text)
    }