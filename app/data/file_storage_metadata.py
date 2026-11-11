import datetime
from dateutil import parser

class File_storage_metadata:
    def __init__(self, file_id: str, original_filename: str, file_extension: str, file_size: int,
                 created_time_stamp: datetime.datetime, content_type: str = ""):
        self.file_id = file_id
        self.original_filename = original_filename.strip()
        self.content_type = content_type.strip()
        self.file_size = file_size
        self.created_time_stamp = created_time_stamp
        self.file_extension = file_extension.strip()
        self.saved_filename = f"{file_id}.{self.file_extension.strip()}"
        self.file_path = f"app/data/files/{self.saved_filename}"

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        """

        Returns: a string representation of the FileStorageMetadata object. Will be in the following format:
        file_id, original_filename, file_extension, file_size, created_time_stamp, content_type

        """
        return f"{self.file_id}, {self.original_filename}, {self.file_extension}, {self.file_size}, {self.created_time_stamp}, {self.content_type}"

    @classmethod
    def from_string(cls, string: str):
        """

        Args:
            string: String retrieved from the metadata file. Will be in the following format:
            file_id, original_filename, file_extension, file_size, created_time_stamp, content_type

        Returns:
            the FileStorageMetadata object created from the metadata file excerpt

        """
        attributes = string.strip().split(",")
        file_id = attributes[0]
        original_filename = attributes[1]
        file_extension = attributes[2]
        file_size = int(attributes[3])
        created_time_stamp = parser.parse(attributes[4])
        if len(attributes) > 5:
            content_type = attributes[5]
        else:
            content_type = ""

        return cls(file_id, original_filename, file_extension, file_size, created_time_stamp, content_type)