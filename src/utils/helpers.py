# Upload model besar dari Google Drive
import os
import gdown

# ID file di Google Drive (model > 25MB, nggak masuk git)
DRIVE_IDS = {
    "src/models/top_model.pkl":    "1DmoOzqmCZIs1yAUXiRsmpDYLg6QcwTPe",
    "src/models/bottom_model.pkl": "1JVcMIrr9mzHcrVNkn0l79S9YmNMskGEI",
}


def ensure_models():
    """Download model dari Drive kalau belum ada di lokal."""
    for path, file_id in DRIVE_IDS.items():
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            print(f"Downloading {path} dari Drive...")
            gdown.download(id=file_id, output=path, quiet=False)
        else:
            print(f"Sudah ada: {path}")
