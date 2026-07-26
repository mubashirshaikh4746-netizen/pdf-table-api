import io
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pypdf

app = FastAPI(
    title="PDF Table Extractor to JSON API",
    description="Extract structured text and tables from PDFs.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "PDF Table Extractor API",
        "version": "1.0.0",
    }


@app.post("/v1/extract-tables")
async def extract_tables_from_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. File must be a PDF."
        )

    try:
        contents = await file.read()
        pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
        pages_data = []

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text() or ""
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            pages_data.append(
                {
                    "page_number": page_num,
                    "lines": lines,
                    "line_count": len(lines),
                }
            )

        return {
            "status": "success",
            "filename": file.filename,
            "total_pages": len(pdf_reader.pages),
            "data": pages_data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process PDF: {str(e)}"
        )
