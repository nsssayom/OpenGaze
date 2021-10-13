import requests
import uuid
import subprocess
import os
import csv
import json
import glob
import shutil
from config import settings


# Utility class for common functions
class Utils:
    # Static method to check if a given image URL is valid
    @staticmethod
    def is_image_url(image_url):
        try:
            # Supported image MIME types
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            r = requests.head(image_url)
            if r.headers["content-type"] in image_formats:
                return True
            return False
        except Exception as e:
            print("Error: ", e)
            return False

    # Static method to download an image from a given URL
    @staticmethod
    def download_image(image_url):
        # Get the image extension
        image_extension = image_url.split(".")[-1]

        # Generate a random filename
        filename = str(uuid.uuid4()) + "." + image_extension
        filepath = "temp/" + filename

        # Download the image
        try:
            r = requests.get(image_url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return filename
        except Exception as e:
            print("Error: ", e)
            return False

    # Static method to run FaceLandMarkImg on a given image
    @staticmethod
    def face_landmark_img(image_path):
        # execute FaceLandMarkImg from current directory
        command = settings.face_landmark_img_exec_command + " -f temp/" \
                 + image_path
        print(command)
        process = subprocess.Popen(command,
                                   cwd=os.path.dirname(
                                       os.path.realpath(__file__)),
                                   shell=True, stdout=subprocess.PIPE)
        process.communicate()[0]

        if process.returncode == 0:
            return True
        return False

    # Static method to check if FaceLandmarkImg found face(s)
    @staticmethod
    def is_face_found(image_path):
        # Check if FaceLandmarkImg found face(s)
        csv_path = "processed/" + image_path.split('.')[0] + ".csv"
        if os.path.isfile(csv_path):

            return True
        return False

    # Static method to get gaze data from the CSV file
    # and convert it to JSON string
    @staticmethod
    def get_gaze_data(image_path):
        # Get the CSV file path
        csv_path = "processed/" + image_path.split('.')[0] + ".csv"

        # Read the CSV file
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(
                csvfile, delimiter=',', skipinitialspace=True)

            # Filter out the rows that have no gaze data
            out = [{"face": row["face"],
                    "confidence": row["confidence"],
                    "gaze_0_x": row["gaze_0_x"],
                    "gaze_0_y": row["gaze_0_y"],
                    "gaze_0_z": row["gaze_0_z"],
                    "gaze_1_x": row["gaze_1_x"],
                    "gaze_1_y": row["gaze_1_y"],
                    "gaze_1_z": row["gaze_1_z"],
                    "gaze_angle_x": row["gaze_angle_x"],
                    "gaze_angle_y": row["gaze_angle_y"],
                    "pose_Tx": row["pose_Tx"],
                    "pose_Ty": row["pose_Ty"],
                    "pose_Tz": row["pose_Tz"],
                    "pose_Rx": row["pose_Rx"],
                    "pose_Ry": row["pose_Ry"],
                    "pose_Rz": row["pose_Rz"],
                    }
                   for row in reader]

            # use gaze_data = list(reader) to get all the rows
            gaze_data = list(out)

        # Convert the gaze data to JSON string
        gaze_data_json = json.loads(json.dumps(gaze_data))
        return gaze_data_json

    # Static method to delete temporary and processed files
    @staticmethod
    def delete_files(image_name):

        image_name = image_name.split('.')[0]

        # Delete files in temp directory
        for filename in glob.glob("temp/" + image_name + "*"):
            try:
                os.remove(filename)
            except IsADirectoryError:
                shutil.rmtree(filename)

        # Delete files in processed directory
        for filename in glob.glob("processed/" + image_name + "*"):
            try:
                os.remove(filename)
            except IsADirectoryError:
                shutil.rmtree(filename)

        return True
