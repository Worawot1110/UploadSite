
from flask import Flask, request, render_template_string
import requests
import urllib.parse
from datetime import datetime

app = Flask(__name__)

# =========================
# NEXTCLOUD CONFIG
# =========================

NEXTCLOUD_URL = "https://cloud.worawut1124it.uk"

NEXTCLOUD_USER = "worawut"

NEXTCLOUD_PASS = "LqEre-XWBG8-QSpJ8-JXTRn-EtMjN"

UPLOAD_FOLDER = "Uploads"
TODAY_FOLDER = datetime.now().strftime("%Y-%m-%d")
# =========================
# HTML
# =========================

HTML = """

<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width, initial-scale=1.0"
>

<title>Upload Center</title>

<script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="bg-gray-100 min-h-screen p-5">

<div
class="max-w-3xl mx-auto bg-white shadow-2xl rounded-3xl p-8"
>

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

<div class="w-full bg-gray-200 rounded-full h-6 mt-6 overflow-hidden">

<div
id="progressBar"
class="bg-blue-600 h-6 text-white text-center text-sm leading-6"
style="width:0%"
>
0%
</div>

</div>

<p
id="uploadStatus"
class="text-center mt-3 text-gray-500"
>
Waiting for upload...
</p>


</form>

{% if files %}

<div class="mt-10 space-y-8">

{% for item in files %}

<div
class="bg-green-50 border border-green-200 rounded-3xl p-5"
>

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

    const tempInput =
        document.createElement("input");

    tempInput.value = url;

    document.body.appendChild(tempInput);

    tempInput.select();

    document.execCommand("copy");

    document.body.removeChild(tempInput);

    alert("Copied URL!");
}

</script>
<script>

const form = document.querySelector("form");

form.addEventListener("submit", function(e) {

    e.preventDefault();

    const files = document.querySelector(
        'input[type="file"]'
    ).files;

    if (files.length === 0) {

        alert("Choose files first");

        return;
    }

    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {

        formData.append("files", files[i]);
    }

    const xhr = new XMLHttpRequest();

    xhr.open("POST", "/", true);

    xhr.upload.addEventListener(
        "progress",
        function(e) {

            if (e.lengthComputable) {

                const percent = Math.round(
                    (e.loaded / e.total) * 100
                );

                const progressBar =
                    document.getElementById(
                        "progressBar"
                    );

                progressBar.style.width =
                    percent + "%";

                progressBar.innerText =
                    percent + "%";

                document.getElementById(
                    "uploadStatus"
                ).innerText =
                    "Uploading...";
            }
        }
    );

    xhr.onload = function() {

        if (xhr.status === 200) {

            document.open();
            document.write(xhr.responseText);
            document.close();

        } else {

            alert("Upload failed");
        }
    };

    xhr.send(formData);

});

</script>
</body>
</html>

"""

# =========================
# ROUTE
# =========================

@app.route("/", methods=["GET", "POST"])

def home():

    uploaded_files = []

    if request.method == "POST":

        files = request.files.getlist("files")

        # Create folder if not exists

        folder_url = (
    f"{NEXTCLOUD_URL}/remote.php/dav/files/"
    f"{NEXTCLOUD_USER}/"
    f"{UPLOAD_FOLDER}/"
    f"{TODAY_FOLDER}"
)

        try:

            requests.request(
                "MKCOL",
                folder_url,
                auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS),
                timeout=30
            )

        except:

            pass

        # Upload files

        for file in files:

            filename = urllib.parse.quote(
                file.filename,
                safe=''
            )

            upload_url = (
    f"{NEXTCLOUD_URL}/remote.php/dav/files/"
    f"{NEXTCLOUD_USER}/"
    f"{UPLOAD_FOLDER}/"
    f"{TODAY_FOLDER}/"
    f"{filename}"
)
            try:

                response = requests.put(
                    upload_url,
                    data=file.read(),
                    auth=(
                    NEXTCLOUD_USER,
                    NEXTCLOUD_PASS
                    ),
                    timeout=1800
                )

                print("UPLOAD STATUS:")
                print(response.status_code)

                print("UPLOAD RESPONSE:")
                print(response.text)

            except Exception as e:

                print(e)
                
                continue

            # Create public share

            if response.status_code in [200, 201, 204]:

                share_api = (
                    f"{NEXTCLOUD_URL}/ocs/v2.php/"
                    f"apps/files_sharing/api/v1/shares"
                )

                try:

                    share_response = requests.post(
                        share_api,
                        auth=(
                            NEXTCLOUD_USER,
                            NEXTCLOUD_PASS
                        ),
                        headers={
                            "OCS-APIRequest": "true",
                            "Accept": "application/json"
                        },
                        data={
                            "path":
f"{UPLOAD_FOLDER}/{TODAY_FOLDER}/{file.filename}",

                            "shareType": 3,

                            "permissions": 1
                        },
                        timeout=60
                    )

                    share_data = (
                        share_response.json()
                    )

                    viewer_link = (
                        share_data["ocs"]["data"]["url"]
                    )

                    preview_link = (
                        viewer_link + "/download"
                    )

                except Exception as e:

                    print(e)

                    viewer_link = (
                        "SHARE API ERROR"
                    )

                    preview_link = ""

                # Check video

                is_video = (
                    file.filename.lower().endswith((
                        ".mp4",
                        ".webm",
                        ".mov",
                        ".mkv"
                    ))
                )

                uploaded_files.append({

                    "filename":
                    file.filename,

                    "viewer":
                    viewer_link,

                    "preview":
                    preview_link,

                    "is_video":
                    is_video
                })

    return render_template_string(
        HTML,
        files=uploaded_files
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
