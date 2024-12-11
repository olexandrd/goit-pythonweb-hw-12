"""
This module provides a service for uploading files to Cloudinary.

Classes:
    UploadFileService: A service class for uploading files to Cloudinary.

Usage Example:
    service = UploadFileService(cloud_name='your_cloud_name', api_key='your_api_key', api_secret='your_api_secret')
    url = service.upload_file(file, username='your_username')

"""

import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    This class provides a method to upload a file to Cloudinary.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Uploads a file to Cloudinary and returns the URL of the uploaded file.

        Args:
            file: The file to be uploaded.
            username: The username to be used in the public ID of the file.

        Returns:
            str: The URL of the uploaded file.

        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
