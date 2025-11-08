import requests

def upload_pdf(file_path, backend_url="http://localhost:3000/api/generate_scene"):
    """
    Mengirim PDF ke backend dan menerima JSON scene.
    
    Parameters:
    -----------
    file_path : str
        Path file PDF yang akan dikirim.
    backend_url : str
        URL endpoint backend yang menerima file PDF.
    
    Returns:
    --------
    dict
        JSON response dari backend. None jika gagal.
    """
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(backend_url, files=files)
            response.raise_for_status()  # cek error HTTP
            return response.json()
    except Exception as e:
        print(f"Gagal upload file: {e}")
        return None


if __name__ == "__main__":
    # Input file PDF
    file_path = input("Masukkan path PDF: ").strip()
    
    # Upload dan terima JSON
    result = upload_pdf(file_path)
    
    if result:
        print("=== JSON dari Backend ===")
        import json
        print(json.dumps(result, indent=4))
    else:
        print("Gagal menerima response dari backend.")
