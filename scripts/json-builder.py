import hashlib
import json
from pathlib import Path
import re

VALID = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff"}
SUFFIX_RE = re.compile(r"_(\d+)px$")

def sha1_of_file(path, chunk_size=8192):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def find_derivative(original_stem, dir_path):
    for p in Path(dir_path).iterdir():
        if not p.is_file():
            continue
        if SUFFIX_RE.sub("", p.stem) == original_stem:
            return p

def add_work(sha, title, tags, src, dim1, dim2):
    return {
        "sha-1": sha,
        "title": title,
        "tags": tags,
        "source image": src,
        "1200px": dim1,
        "800px": dim2
    }

def main():

    works = []
    json_path = Path("works.json")

    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                works = json.load(f)
            except json.JSONDecodeError:
                works = []

    existing_shas = {item.get("sha-1") for item in works if isinstance(item, dict)}

    source_folder = Path("img/original")

    for i in source_folder.iterdir():
        if not i.is_file():
            continue
        if i.suffix.lower() not in VALID:
            continue

        # print(i)
        
        sha = sha1_of_file(i)
        if sha in existing_shas:
            continue

        title = ""
        tags = []
        src = str(i)
        stem = i.stem

        # ensure find_derivative accepts Path and dir exists
        dim1 = find_derivative(stem, Path("img/1200px"))
        dim2 = find_derivative(stem, Path("img/800px"))

        # if find_derivative returns Path, convert to str for JSON
        if dim1 is not None:
            dim1 = str(dim1)
        if dim2 is not None:
            dim2 = str(dim2)


        works.append(add_work(sha, title, tags, src, dim1, dim2))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(works, f, indent=2, ensure_ascii=False)

    # print(json.dumps(works, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
