from getpass import getpass
import subprocess
import shutil
import pandas
import os
import collections
import openpyxl
from pathlib import Path
from email.header import decode_header
import json
import pandas as pd
import pyarrow

HERE = Path(__file__).parent
RSCRIPT_EXE = shutil.which("Rscript") or "/usr/local/bin/Rscript"

temp_data_dir = ".temp_data"

Credentials = collections.namedtuple("Credentials", ["username", "password"])

class CommandLineCredentialFetcher:
    def fetch_credentials(self):
        username = input("Enter email for Objective Connect account: ")
        password = getpass("Enter password: ")
        return Credentials(username=username, password=password) 
    
class Objr:
    def __init__(self, credential_fetcher):
        self.credential_fetcher = credential_fetcher

    def download(self, file_list: list, filetypes: list, file_names: list, rscript: str):

            credentials = self.credential_fetcher.fetch_credentials()

            dataframe_dict = {}

            try:
    
                for idx, key in enumerate(file_list):

                    os.makedirs(temp_data_dir, exist_ok=True)

                    filename_uuid = file_list[idx]
                    filetype = filetypes[idx]
                    filename = file_names[idx]

                    subprocess.run([RSCRIPT_EXE, str(HERE/rscript), filename_uuid, temp_data_dir],
                                env = {"OBJR_USR": credentials.username, "OBJR_PWD": credentials.password},
                                check=True,
                                capture_output=True)
                    files = os.listdir(temp_data_dir)
                    if len(files) != 1:
                        raise Exception(f"There should be only 1 file in the {temp_data_dir} folder")
                    file = files[0]
                    if filetype == "xlsx":
                                    dataframe_dict[filename] =  pandas.read_excel(os.path.join(temp_data_dir, file))
                    elif filetype == "csv":
                                    dataframe_dict[filename] = pandas.read_csv(os.path.join(temp_data_dir, file), dayfirst = True)
                    elif filetype == "parquet":
                                    dataframe_dict[filename]  = pandas.read_parquet(os.path.join(temp_data_dir, file))
                    elif filetype == "py":

                        file_list_paths = [f for f in Path(temp_data_dir).iterdir() if f.is_file()]
                        src = file_list_paths[0]
                        clean_name = decode_filename(src.name)
                        dst = Path.cwd() / clean_name

                        shutil.copy(src, dst)

                    else:
                        raise ValueError(f"Unsupported filetype: {filetype}")
                            
                    shutil.rmtree(temp_data_dir)

                return dataframe_dict
            
            finally:
                if Path(temp_data_dir).exists():
                    shutil.rmtree(temp_data_dir)

    def upload(self, workspace_uuid: str, folder_uuid:str, filename: str):
          try:
            credentials = self.credential_fetcher.fetch_credentials()
            subprocess.run([RSCRIPT_EXE, str(HERE/"oc_upload_data.r"), workspace_uuid, folder_uuid, filename],
                env = {"OBJR_USR": credentials.username, "OBJR_PWD": credentials.password},
                check=True,
                capture_output=True)
          except:
                print("Something went wrong")

    def upload_new_version(self, filepath: str, file_uuid: str):
           try:
            credentials = self.credential_fetcher.fetch_credentials()
            subprocess.run([RSCRIPT_EXE, str(HERE/"oc_upload_new_version.r"), filepath, file_uuid],
                env = {"OBJR_USR": credentials.username, "OBJR_PWD": credentials.password},
                check=True,
                capture_output=True)
           except:
                  print("Something went wrong")

    def get_version_info(self, file_list: list, file_names: list):
        credentials = self.credential_fetcher.fetch_credentials()

        dataframe_dict = {}

        try:
            for idx, key in enumerate(file_list):

                file_uuid = file_list[idx]
                filename = file_names[idx]

                result = subprocess.run(["/usr/local/bin/Rscript", "oc_get_version_info.r", file_uuid],
                                        env = {"OBJR_USR": credentials.username, "OBJR_PWD": credentials.password},
                                        check=True,
                                        capture_output=True)
                data = json.loads(result.stdout)
                df = pd.DataFrame(data)
                dataframe_dict[filename] = df
            return dataframe_dict

        except:
            print("Something went wrong")

def decode_filename(name: str):
    decoded_parts = decode_header(name)
    decoded, encoding = decoded_parts[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8")
    return decoded
    
def get_objr_data(uuids: list, filetypes: list, file_names: list):
    credential_fetching_method = CommandLineCredentialFetcher()
    objr = Objr(credential_fetcher=credential_fetching_method)
    return objr.download(uuids, filetypes, file_names, rscript = "oc_download_data.r")

def get_objr_data_version(uuids: list, filetypes: list, file_names: list):
    credential_fetching_method = CommandLineCredentialFetcher()
    objr = Objr(credential_fetcher=credential_fetching_method)
    return objr.download(uuids, filetypes, file_names, rscript = "oc_download_version.r")

def upload_data_to_oc(workspace_uuid: str, folder_uuid: str, filename: str):
    credential_fetching_method = CommandLineCredentialFetcher()
    objr = Objr(credential_fetcher=credential_fetching_method)
    return objr.upload(workspace_uuid, folder_uuid, filename)

def upload_version_to_oc(filepath: str, file_uuid: str):
    credential_fetching_method = CommandLineCredentialFetcher()
    objr = Objr(credential_fetcher=credential_fetching_method)
    return objr.upload_new_version(filepath, file_uuid)

def print_version_info(uuids: list, file_names: list):
    credential_fetching_method = CommandLineCredentialFetcher()
    objr = Objr(credential_fetcher=credential_fetching_method)
    return objr.get_version_info(uuids, file_names)
