from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/")
async def root():
    html = """
         <!DOCTYPE html>
         <html>
             <body>
               <h1>
               Marias server running
               </h1>
         </html>
         """

    return HTMLResponse(html)
