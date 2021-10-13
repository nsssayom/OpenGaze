import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# import CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from utils import Utils
from pydantic import BaseModel


class Image(BaseModel):
    image_url: str


app = FastAPI()

# origins = [
#     "http://localhost",
#     "http://localhost:8080",
# ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()


def auth(credentials:
         HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(
        credentials.username, settings.api_key)
    correct_password = secrets.compare_digest(
        credentials.password, settings.api_secret)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True


@app.post("/")
def post_image(image: Image, auth_success: bool = Depends(auth)):
    if (Utils.is_image_url(image.image_url)):
        image_name = Utils.download_image(image.image_url)

        # If image could not be downloaded
        if not image_name:
            if not settings.debug:
                Utils.delete_files(image_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unreachable image resource",
            )

        # If image was downloaded successfully run faceLandmarkImg
        if Utils.face_landmark_img(image_name):
            if Utils.is_face_found(image_name):
                json_data = Utils.get_gaze_data(image_name)
                # If DEBUG is false, delete the image
                if not settings.debug:
                    Utils.delete_files(image_name)
                return json_data

        # If no face was found delete the image and return error
        if not settings.debug:
            Utils.delete_files(image_name)
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No face was found",
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image url",
        )
