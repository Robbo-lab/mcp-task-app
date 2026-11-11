import datetime
from pathlib import Path
from uuid import uuid4
import aiofile
from datetime import datetime

from app.models.file_storage_metadata import File_storage_metadata


class LocalStorage:
    def __init__(self):
        pass

    FILE_PATH = Path("../data/files")
    FILE_PATH.mkdir(parents=True, exist_ok=True)
    META_PATH = Path("../data/meta.txt")

    def record_file_changes(self, file_meta_data, action):
        if action == "save":
            with open(f"{self.META_PATH}", "a") as meta_file:
                line = f"{file_meta_data}\n"
                meta_file.write(line)

        elif action == "delete":
            with open(f"{self.META_PATH}", "r") as meta_file:
                all_files = meta_file.readlines()

                filtered_files = [line for line in all_files if line != file_meta_data]
            with open(f"{self.META_PATH}", "w") as meta_file:
                meta_file.writelines(filtered_files)

        else:
            raise ValueError(f"record_file_changes: Invalid action: {action}")

    def find_file_metadata(self, file_id):
        with open(f"{self.META_PATH}", "r") as meta_file:
            all_files = meta_file.readlines()
            file_meta_data = ""
            search_term = f"{{'File_Id': {file_id}"
            for line in all_files:
                if line.startswith(search_term):
                    file_meta_data = line
                    break

            if file_meta_data == "":
                raise ValueError(f"find_file_metadata: No file data found")
            else:
                print(file_meta_data)
                return file_meta_data

    def create_metadata(self, uploaded_file):
        ext = Path(uploaded_file.filename).suffix
        file_id = str(uuid4())
        file_size = uploaded_file.file.size
        original_filename = uploaded_file.filename
        created_datetime = datetime.now()

        metadata = File_storage_metadata(file_id, original_filename, ext, file_size, created_datetime)
        return metadata

    def delete_file(self, file_id):
        metadata = self.find_file_metadata(file_id)
        file_path = Path(f"{self.FILE_PATH}/{metadata.saved_filename}")

        if file_path.is_file():
            file_path.unlink()
        else:
            raise ValueError(f"delete_file: File {metadata.saved_filename} does not exist")

    async def save_file(self, uploaded_file):
        #TODO create a check for matching ids in the metafile
        file_metadata = self.create_metadata(uploaded_file)
        filename = f"{file_metadata["File_Id"]}.{file_metadata["File_extension"]}"
        destination = LocalStorage.FILE_PATH / filename

        destination.parent.mkdir(parents=True, exist_ok=True)

        async with aiofile.AIOFile(destination, "wb") as file:
            while content := await file.read(1024 * 1024):
                await file.write(content)

        self.record_file_changes(file_metadata, "save")
        print(f"{file_metadata['Original_saved']} saved")

#TODO Create Local Storage Class - singleton(?)
#TODO Create FileMetaData Class- Properties: fileId, originalFileName, storedFileName, contentType, fileSize, createdTimeStamp.
#TODO Create functions for LocalStorage - Save, delete, find file path, find file metadata by id, findMaximumId(?)
#TODO Create Tests
