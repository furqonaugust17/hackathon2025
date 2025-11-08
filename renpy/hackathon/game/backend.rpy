init python:
    import requests

    def upload_pdf(file_path):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post("http://localhost:3000/generate-quiz", files=files)
            return response.json()
