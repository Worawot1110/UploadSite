from flask import Flask, request, render_template_string
import requests
import urllib.parse

app = Flask(__name__)

NEXTCLOUD_URL = "https://cloud.worawut1124it.uk"

NEXTCLOUD_USER = "admin"
NEXTCLOUD_PASS = "e3QHm-zfTpt-H54GQ-EdKqE-iDpKT"

UPLOAD_FOLDER = "PublicMedia"

HTML = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Upload Center</title>

<script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="bg-gray-100 min-h-screen p-5">

<div class="max-w-3xl mx-auto bg-white shadow-2xl rounded-3xl p-8">

<h1 class="text-4xl font-bold text-center mb-2">
Upload Photos & Videos
</h1>

<p class="text-center text-gray-500 mb-8">
Upload directly to Nextcloud
</p>

<form
method="POST"
enctype="multipart/form-data"
>

<input
name="files"
type="file"
multiple
class="block w-full border rounded-2xl p-4 mb-4"
/>

<button
type="submit"
class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-2xl transition"
>
Upload Files
</button>

</form>

{% if files %}

<div class="mt-10 space-y-8">

{% for item in files %}

<div class="bg-green-50 border border-green-200 rounded-3xl p-5">

<p class="text-green-700 font-bold text-lg">
Upload Complete
</p>

<input
value="{{ item.viewer }}"
readonly
class="w-full mt-3 border rounded-xl p-3 text-sm bg-white"
/>

<div class="flex gap-3 mt-4 flex-wrap">

<button
type="button"
onclick="copyURL('{{ item.viewer }}')"
class="bg-black text-white px-5 py-2 rounded-xl"
>
Copy URL
</button>

<a
href="{{ item.viewer }}"
target="_blank"
class="bg-blue-600 text-white px-5 py-2 rounded-xl"
>
Open
</a>

</div>

{% if item.is_video %}

<video
controls
playsinline
class="w-full rounded-2xl mt-5 bg-black"
>
<source src="{{ item.preview }}">
</video>

{% else %}

<img
src="{{ item.preview }}"
class="w-full rounded-2xl mt-5"
/>

{% endif %}

</div>

{% endfor %}

</div>

{% endif %}

</div>

<script>

function copyURL(url) {

    navigator.clipboard.writeText(url);

    alert("Copied URL!");
}

</script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():

    uploaded_files = []

    if request.method == "POST":

        files = request.files.getlist("files")

        folder_url = (
            f"{NEXTCLOUD_URL}/remote.php/dav/files/"
            f"{NEXTCLOUD_USER}/{UPLOAD_FOLDER}"
        )

        try:

            requests.request(
                "MKCOL",
                folder_url,
                auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS),
                timeout=30
            )

        except Exception as e:

            print("FOLDER ERROR:")
            print(e)

        for file in files:

            filename = urllib.parse.quote(
                file.filename,
                safe=''
            )

            upload_url = (
                f"{NEXTCLOUD_URL}/remote.php/dav/files/"
                f"{NEXTCLOUD_USER}/"
                f"{UPLOAD_FOLDER}/{filename}"
            )

            try:

                response = requests.put(
                    upload_url,
                    data=file.read(),
                    auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS),
                    timeout=300
                )

            except Exception as e:

                print("UPLOAD ERROR:")
                print(e)

                continue

            if response.status_code in [200, 201, 204]:

                share_api = (
                    f"{NEXTCLOUD_URL}/ocs/v2.php/"
                    f"apps/files_sharing/api/v1/shares"
                )

                try:

                    share_response = requests.post(
                        share_api,
                        auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS),
                        headers={
                            "OCS-APIRequest": "true",
                            "Accept": "application/json"
                        },
                        data={
                            "path": f"/{UPLOAD_FOLDER}/{file.filename}",
                            "shareType": 3,
                            "permissions": 1
                        },
                        timeout=60
                    )

                    print("SHARE STATUS:")
                    print(share_response.status_code)

                    print("SHARE TEXT:")
                    print(share_response.text)

                    share_data = share_response.json()

                    viewer_link = (
                        share_data["ocs"]["data"]["url"]
                    )

                    preview_link = (
                        viewer_link + "/download"
                    )

                except Exception as e:

                    print("SHARE ERROR:")
                    print(e)

                    viewer_link = "SHARE API ERROR"

                    preview_link = ""

                is_video = file.filename.lower().endswith((
                    ".mp4",
                    ".webm",
                    ".mov",
                    ".mkv"
                ))

                uploaded_files.append({
                    "filename": file.filename,
                    "viewer": viewer_link,
                    "preview": preview_link,
                    "is_video": is_video
                })

    return render_template_string(
        HTML,
        files=uploaded_files
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )
