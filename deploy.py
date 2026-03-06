#!/usr/bin/env python3
import hashlib, json, os, sys
import urllib.request, urllib.error

TOKEN        = "[VERCEL_TOKEN]"
TEAM_ID      = "[VERCEL_TEAM_ID]"
PROJECT_NAME = "loan-file-prep"
DEPLOY_DIR   = os.path.dirname(os.path.abspath(__file__))
HEADERS      = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/octet-stream"}

def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f: h.update(f.read())
    return h.hexdigest()

def upload(path, filename):
    with open(path, 'rb') as f: content = f.read()
    s = sha1(path)
    req = urllib.request.Request("https://api.vercel.com/v2/files", data=content,
        headers={**HEADERS, "x-vercel-digest": s})
    try:
        urllib.request.urlopen(req)
        print(f"  ✓ {filename}")
    except urllib.error.HTTPError as e:
        if e.code != 409: print(f"  ✗ {filename}: {e.code}"); return None, None
        print(f"  ✓ {filename} (cached)")
    return s, len(content)

def create_deploy(files):
    url = f"https://api.vercel.com/v13/deployments?teamId={TEAM_ID}"
    payload = {"name": PROJECT_NAME, "files": files,
        "projectSettings": {"framework": None, "buildCommand": None, "outputDirectory": None},
        "target": "production"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r: return json.loads(r.read())

deploy_files = ["index.html", "vercel.json"]

print("Uploading files...")
refs = []
for f in deploy_files:
    s, sz = upload(os.path.join(DEPLOY_DIR, f), f)
    if s: refs.append({"file": f, "sha": s, "size": sz})

print("\nDeploying...")
result = create_deploy(refs)
print(f"\n🌐 LIVE: https://{result['url']}")
