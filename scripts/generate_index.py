import os
import json
import zipfile
import hashlib

PACKAGES_DIR = "packages"
OUTPUT_FILE = "index.json"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def read_package_json(zip_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open("package.json") as f:
            return json.loads(f.read().decode("utf-8"))

index = {
    "packages": {}
}

for file in os.listdir(PACKAGES_DIR):
    if not file.endswith(".kpak"):
        continue

    full_path = os.path.join(PACKAGES_DIR, file)
    zip_hash = sha256_file(full_path)

    try:
        meta = read_package_json(full_path)
    except Exception as e:
        print(f"Skipping {file}, invalid package.json: {e}")
        continue

    pkg_id = meta.get("packageIdentity") or meta.get("id")
    version = meta.get("packageVersion", "0.0.0")

    if pkg_id not in index["packages"]:
        index["packages"][pkg_id] = {
            "displayName": meta.get("displayName"),
            "author": meta.get("author"),
            "versions": {}
        }

    index["packages"][pkg_id]["versions"][version] = {
        "file": f"packages/{file}",
        "sha256": zip_hash,
        "targetKoilVersion": meta.get("targetKoilVersion"),
        "authorId": meta.get("authorId")
    }

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2)

print("index.json generated successfully")
