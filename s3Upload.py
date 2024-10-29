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

def create_s3_folder(folder_path):
  # Check if the folder already exists
  try:
    result = S3_CLIENT.list_objects_v2(Bucket=BUCKET, Prefix=folder_path, MaxKeys=1)

    if 'Contents' in result:
      return False
    else:
      # Create the folder by uploading an empty object with the folder path
      S3_CLIENT.put_object(Bucket=BUCKET, Key=folder_path)
      return True
    
  except any as e:
    print(f"Something went wrong creating folder {folder_path}:\n{e}")
    exit()

def compress_and_upload_folder(folder_path):
  # Compress the folder
  with zipfile.ZipFile(ZIP_FILE_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:

    for root, dirs, files in os.walk(folder_path):

      for file in files:

        file_path = os.path.join(root, file)
        # Write each file to the zip file
        zipf.write(file_path, os.path.relpath(file_path, folder_path))
        
  print(f"Folder '{folder_path}' compressed into '{ZIP_FILE_NAME}'.")
  print(LOADING_MSG)

  # Define full S3 path
  s3_full_path = f"{folder_path.rstrip('/')}/{ZIP_FILE_NAME}"

  # Upload compressed file to S3
  S3_CLIENT = boto3.client('s3')
  try:
    S3_CLIENT.upload_file(ZIP_FILE_NAME, BUCKET, s3_full_path)
    print(f"File '{ZIP_FILE_NAME}' uploaded to 's3://{BUCKET}/{s3_full_path}'.")
    print(LOADING_MSG)
    
  except any as e:
    print(f"Something went wrong uploading {ZIP_FILE_NAME}:\n{e}")
    exit()

  # Remove local zip file after uploading
  os.remove(ZIP_FILE_NAME)
  print(f"Local zip file '{ZIP_FILE_NAME}' removed after upload.")


folders_list = find_data_folders()

print("Pick a folder to upload to S3:")
for i, folder in enumerate(folders_list):
  if (check_s3_folder(folder)):
    print(f"({i}) [EXISTS on S3] {folder}")
  else :
    print(f"({i}) [NOT on S3] {folder}")

print("\nWhich folder would you like to upload to S3?")
option = int(input("Enter the folder number: "))

if (option < 0 or option >= len(folders_list)):
  print(f"Aborting actions, option {option} is not valid.")
  exit()

target_folder = folders_list[option]

if not os.path.isfile(os.path.join(target_folder, '.gitignore')):
  print("Aborting actions, please make sure you include .gitignore as specified in the README.md")
  exit()

print(f"\nAre you sure you want to upload ({option}) {folders_list[option]}")
if (input("Type \"confirm\" to proceed: ") != "confirm"):
  print("Aborting actions, \"confirm\" was not typed.")
  exit()

print(LOADING_MSG)

if (not check_s3_folder(target_folder)):
  try:
    S3_CLIENT.put_object(Bucket=BUCKET, Key=target_folder)
  except any as e:
    print(f"Something went wrong creating folder {target_folder}:\n{e}")
    exit()

compress_and_upload_folder(target_folder)