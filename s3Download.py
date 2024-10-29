import boto3
import os
import zipfile
from botocore.exceptions import NoCredentialsError, ClientError

S3_CLIENT = boto3.client('s3')
BUCKET = "delaynomore-notebooks"
ZIP_FILE_NAME = "data.zip"
LOADING_MSG = "\n------------------------------------------\nLoading... please wait until program exits\n------------------------------------------\n"

def find_data_folders(root_dir='.'):
  data_folders = []

  # Walk through directory structure
  for dirpath, dirnames, filenames in os.walk(root_dir):
    # Check if there's 'data' folder in the current directory
    if 'data' in dirnames:
      data_folder_path = os.path.join(dirpath, 'data')
      data_folders.append("/".join(data_folder_path.split('/')[1:]) + "/")

  return data_folders

def check_s3_folder(folder_path):
  # Check if the folder already exists
  try:
    result = S3_CLIENT.list_objects_v2(Bucket=BUCKET, Prefix=folder_path, MaxKeys=1)

    if 'Contents' in result:
      return True
    else:
      return False
    
  except any as e:
    print(f"Something went wrong checking folder {folder_path}:\n{e}")
    exit()

def download_folder(folder_path):
  # Delete existing data files
  for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    try:
      if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except any as e:
      print(f"Something went wrong deleting {file_path}:\n{e}")
  print(LOADING_MSG)

  # Download from S3
  full_path = f"{folder_path.rstrip('/')}/{ZIP_FILE_NAME}"
  try:
    S3_CLIENT.download_file(BUCKET, full_path, full_path)
    print(f"Downloaded {ZIP_FILE_NAME} file from {full_path}")
  except ClientError as e:
    print(f"Something went wrong downloading from {full_path}:\n{e}")
  print(LOADING_MSG)

  # Unzip file
  with zipfile.ZipFile(full_path, 'r') as zip_ref:
    zip_ref.extractall(folder_path)
    print(f"Extracted {ZIP_FILE_NAME}")
  print(LOADING_MSG)

  # Delete .zip
  try:
    os.remove(full_path)
  except any as e:
      print(f"Error deleting {full_path}: {e}")


folders_list = find_data_folders()
folders_on_s3 = []
folders_not_on_s3 = []

for folder in folders_list:
  if (check_s3_folder(folder)):
    folders_on_s3.append(folder) 
  else :
    folders_not_on_s3.append(folder)

print("Pick a folder to download from S3:")
for i, folder in enumerate(folders_on_s3):
  print(f"({i}) {folder}")

if folders_not_on_s3:
  print("\nThe following are folders that are not in S3:")
  for folder in folders_not_on_s3 :
    print(folder)
  print("\nThe owner of that folder might have no uploaded their data folder, please remind them.")

print("\nWhich folder would you like to download from S3?")
option = int(input("Enter the folder number: "))

if (option < 0 or option >= len(folders_on_s3)):
  print(f"Aborting actions, option {option} is not valid.")
  exit()

target_folder = folders_on_s3[option]

print(f"\nBy downloading to {target_folder} you are deleting all existing files within. Are you sure you want proceed?")
if (input("Type \"confirm\" to proceed: ") != "confirm"):
  print("Aborting actions, \"confirm\" was not typed.")
  exit()

print(LOADING_MSG)

download_folder(folders_on_s3[option])