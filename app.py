from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image_9.png-3ba70514-c684-4f37-83e8-98896114009a.png"
)


def resolve_bg_image() -> Path | None:
    candidates = [
PROJECT_DIR / "image_9.png.png"
    
        EXTERNAL_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background: #000;
            overflow: hidden;
        }

        .scene {
            position: fixed;
            inset: 0;
            background-image: url("{{ url_for('background_image') }}");
            background-size: 100% 100%;
            background-repeat: no-repeat;
            background-position: top center;
            background-attachment: fixed;
        }

        .overlay {
            position: absolute;
            left: 17.0%;
            top: 30.9%;
            width: 16.9%;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .input-row {
            position: relative;
            width: 100%;
        }

        .retro-input,
        .retro-output {
            width: calc(100% - 33px);
            height: 28px;
            border-radius: 9px;
            border: 1px solid transparent;
            background: transparent; /* tamamen transparan */
            color: #000000; /* yazi siyah */
            font-family: inherit;
            font-size: clamp(6px, 0.6vw, 8px);
            letter-spacing: 0.2px;
            text-shadow: none;
        }

        .retro-input {
            padding: 0 8px;
            outline: none;
        }

        .retro-input::placeholder {
            color: #222222;
        }

        .enter-btn {
            position: absolute;
            right: -30px;
            top: -1px;
            width: 31px;
            height: 31px;
            border-radius: 50%;
            border: 1px solid rgba(191, 236, 255, 0.95);
            background: linear-gradient(180deg, #7ad8ff 0%, #3baee8 52%, #1f87c4 100%);
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: clamp(5px, 0.5vw, 7px);
            padding: 0;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 70, 109, 0.8),
                0 2px 0 rgba(9, 70, 109, 0.65);
        }

        .enter-btn:active {
            transform: translateY(1px);
        }

        .retro-output {
            margin-top: 2px; /* alt kutu biraz asagi */
            display: flex;
            align-items: center;
            padding: 0 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .retro-output a {
            color: #000000;
            text-decoration: none;
        }

        .retro-output a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="scene">
        <form id="shortenerForm" class="overlay" autocomplete="off">
            <div class="input-row">
                <input id="longUrl" class="retro-input" type="url" required placeholder="https://...">
                <button class="enter-btn" type="submit">Enter</button>
            </div>
            <div id="shortResult" class="retro-output">short link</div>
        </form>
    </div>

    <script>
        (function () {
            const form = document.getElementById("shortenerForm");
            const longUrlInput = document.getElementById("longUrl");
            const shortResult = document.getElementById("shortResult");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = longUrlInput.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        shortResult.textContent = data.error || "işlem başarısız";
                        return;
                    }

                    shortResult.innerHTML =
                        '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' +
                        data.short_url +
                        "</a>";
                } catch (error) {
                    shortResult.textContent = "ağ hatası";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_bg_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    payload = request.get_json(silent=True) or {}
    long_url = (payload.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/<code>", methods=["GET"])
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image_9.png-3ba70514-c684-4f37-83e8-98896114009a.png"
)


def resolve_bg_image() -> Path | None:
    candidates = [
       PROJECT_DIR / "image_9.png.png",
        EXTERNAL_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background: #000;
            overflow: hidden;
        }

        .scene {
            position: fixed;
            inset: 0;
            background-image: url("{{ url_for('background_image') }}");
            background-size: 100% 100%;
            background-repeat: no-repeat;
            background-position: top center;
            background-attachment: fixed;
        }

        .overlay {
            position: absolute;
            left: 17.0%;
            top: 30.9%;
            width: 16.9%;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .input-row {
            position: relative;
            width: 100%;
        }

        .retro-input,
        .retro-output {
            width: calc(100% - 33px); /* genislik artti */
            height: 28px; /* istedigin deger */
            border-radius: 9px;
            border: 1px solid transparent;
            background: rgba(236, 248, 255, 0.23);
            color: #ffffff;
            font-family: inherit;
            font-size: clamp(6px, 0.6vw, 8px);
            letter-spacing: 0.2px;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.38);
            backdrop-filter: blur(1px);
        }

        .retro-input {
            padding: 0 8px;
            outline: none;
        }

        .retro-input::placeholder {
            color: rgba(246, 252, 255, 0.94);
        }

        .enter-btn {
            position: absolute;
            right: -2px; /* saga biraz kaydi */
            top: -1px;
            width: 31px;
            height: 31px;
            border-radius: 50%;
            border: 1px solid rgba(191, 236, 255, 0.95);
            background: linear-gradient(180deg, #7ad8ff 0%, #3baee8 52%, #1f87c4 100%);
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: clamp(5px, 0.5vw, 7px);
            padding: 0;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 70, 109, 0.8),
                0 2px 0 rgba(9, 70, 109, 0.65);
        }

        .enter-btn:active {
            transform: translateY(1px);
        }

        .retro-output {
            margin-top: -3px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .retro-output a {
            color: #f2fbff;
            text-decoration: none;
        }

        .retro-output a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="scene">
        <form id="shortenerForm" class="overlay" autocomplete="off">
            <div class="input-row">
                <input id="longUrl" class="retro-input" type="url" required placeholder="https://...">
                <button class="enter-btn" type="submit">Enter</button>
            </div>
            <div id="shortResult" class="retro-output">kısa link burada görünecek</div>
        </form>
    </div>

    <script>
        (function () {
            const form = document.getElementById("shortenerForm");
            const longUrlInput = document.getElementById("longUrl");
            const shortResult = document.getElementById("shortResult");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = longUrlInput.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        shortResult.textContent = data.error || "işlem başarısız";
                        return;
                    }

                    shortResult.innerHTML =
                        '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' +
                        data.short_url +
                        "</a>";
                } catch (error) {
                    shortResult.textContent = "ağ hatası";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_bg_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    payload = request.get_json(silent=True) or {}
    long_url = (payload.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/<code>", methods=["GET"])
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image_9.png-3ba70514-c684-4f37-83e8-98896114009a.png"
)


def resolve_bg_image() -> Path | None:
    candidates = [
        PROJECT_DIR / "image_9.png",
        PROJECT_DIR / "static" / "image_9.png",
        EXTERNAL_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background: #000;
            overflow: hidden;
        }

        .scene {
            position: fixed;
            inset: 0;
            background-image: url("{{ url_for('background_image') }}");
            background-size: 100% 100%;
            background-repeat: no-repeat;
            background-position: top center;
            background-attachment: fixed;
        }

        .overlay {
            position: absolute;
            left: 17.0%;
            top: 30.9%;
            width: 16.9%;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .input-row {
            position: relative;
            width: 100%;
        }

        .retro-input,
        .retro-output {
            width: calc(100% - 38px); /* kutulari kisalt */
            height: 34px; /* boyu kisalt */
            border-radius: 9px;
            border: 1px solid transparent;
            background: rgba(236, 248, 255, 0.23);
            color: #ffffff;
            font-family: inherit;
            font-size: clamp(6px, 0.6vw, 8px);
            letter-spacing: 0.2px;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.38);
            backdrop-filter: blur(1px);
        }

        .retro-input {
            padding: 0 8px;
            outline: none;
        }

        .retro-input::placeholder {
            color: rgba(246, 252, 255, 0.94);
        }

        .enter-btn {
            position: absolute;
            right: 0;
            top: 1px;
            width: 31px;
            height: 31px;
            border-radius: 50%;
            border: 1px solid rgba(191, 236, 255, 0.95);
            background: linear-gradient(180deg, #7ad8ff 0%, #3baee8 52%, #1f87c4 100%);
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: clamp(5px, 0.5vw, 7px);
            padding: 0;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 70, 109, 0.8),
                0 2px 0 rgba(9, 70, 109, 0.65);
        }

        .enter-btn:active {
            transform: translateY(1px);
        }

        .retro-output {
            height: 34px;
            margin-top: -1px; /* alttaki kutuyu biraz yukari al */
            display: flex;
            align-items: center;
            padding: 0 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .retro-output a {
            color: #f2fbff;
            text-decoration: none;
        }

        .retro-output a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="scene">
        <form id="shortenerForm" class="overlay" autocomplete="off">
            <div class="input-row">
                <input id="longUrl" class="retro-input" type="url" required placeholder="https://...">
                <button class="enter-btn" type="submit">Enter</button>
            </div>
            <div id="shortResult" class="retro-output">kısa link burada görünecek</div>
        </form>
    </div>

    <script>
        (function () {
            const form = document.getElementById("shortenerForm");
            const longUrlInput = document.getElementById("longUrl");
            const shortResult = document.getElementById("shortResult");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = longUrlInput.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        shortResult.textContent = data.error || "işlem başarısız";
                        return;
                    }

                    shortResult.innerHTML =
                        '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' +
                        data.short_url +
                        "</a>";
                } catch (error) {
                    shortResult.textContent = "ağ hatası";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_bg_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    payload = request.get_json(silent=True) or {}
    long_url = (payload.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/<code>", methods=["GET"])
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)

# In-memory URL storage
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image_9.png-3ba70514-c684-4f37-83e8-98896114009a.png"
)


def resolve_bg_image() -> Path | None:
    candidates = [
        PROJECT_DIR / "image_9.png",
        PROJECT_DIR / "static" / "image_9.png",
        EXTERNAL_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background: #000;
            overflow: hidden;
        }

        /* Full-screen, fixed, no-repeat background */
        .scene {
            position: fixed;
            inset: 0;
            background-image: url("{{ url_for('background_image') }}");
            background-size: 100% 100%;
            background-repeat: no-repeat;
            background-position: top center;
            background-attachment: fixed;
        }

        /*
          Fine-tuned monitor alignment:
          - moved up and slightly right
          - reduced widths
          - increased heights
        */
        .overlay {
            position: absolute;
            left: 17.0%;
            top: 30.9%;
            width: 16.9%;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .input-row {
            display: grid;
            grid-template-columns: 1fr 30px;
            gap: 7px;
            align-items: center;
        }

        .retro-input,
        .retro-output {
            width: 100%;
            height: 38px;
            border-radius: 9px;
            border: 1px solid transparent; /* requested transparent border */
            background: rgba(236, 248, 255, 0.23);
            color: #ffffff;
            font-family: inherit;
            font-size: clamp(6px, 0.6vw, 8px);
            letter-spacing: 0.2px;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.38);
            backdrop-filter: blur(1px);
        }

        .retro-input {
            padding: 0 8px;
            outline: none;
        }

        .retro-input::placeholder {
            color: rgba(246, 252, 255, 0.94);
        }

        .enter-btn {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            border: 1px solid rgba(191, 236, 255, 0.95);
            background: linear-gradient(180deg, #7ad8ff 0%, #3baee8 52%, #1f87c4 100%);
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: clamp(5px, 0.5vw, 7px);
            padding: 0;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 70, 109, 0.8),
                0 2px 0 rgba(9, 70, 109, 0.65);
        }

        .enter-btn:active {
            transform: translateY(1px);
        }

        .retro-output {
            display: flex;
            align-items: center;
            padding: 0 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .retro-output a {
            color: #f2fbff;
            text-decoration: none;
        }

        .retro-output a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="scene">
        <form id="shortenerForm" class="overlay" autocomplete="off">
            <div class="input-row">
                <input id="longUrl" class="retro-input" type="url" required placeholder="https://...">
                <button class="enter-btn" type="submit">Enter</button>
            </div>
            <div id="shortResult" class="retro-output">kısa link burada görünecek</div>
        </form>
    </div>

    <script>
        (function () {
            const form = document.getElementById("shortenerForm");
            const longUrlInput = document.getElementById("longUrl");
            const shortResult = document.getElementById("shortResult");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = longUrlInput.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        shortResult.textContent = data.error || "işlem başarısız";
                        return;
                    }

                    shortResult.innerHTML =
                        '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' +
                        data.short_url +
                        "</a>";
                } catch (error) {
                    shortResult.textContent = "ağ hatası";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_bg_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    payload = request.get_json(silent=True) or {}
    long_url = (payload.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/<code>", methods=["GET"])
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)

# RAM storage
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image_9.png-0f4f5dc3-60b8-4dc3-bdf3-6ce147c0c01e.png"
)


def resolve_bg_image() -> Path | None:
    candidates = [
        PROJECT_DIR / "image_9.png",
        PROJECT_DIR / "static" / "image_9.png",
        EXTERNAL_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background: #000;
            overflow: hidden;
        }

        /*
          Image ratio: 1024 x 576.
          This keeps the entire image visible (no crop), top aligned, no repeat.
        */
        .scene {
            position: fixed;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: min(100vw, calc(100vh * 1.7777778));
            aspect-ratio: 1024 / 576;
            background-image: url("{{ url_for('background_image') }}");
            background-size: 100% 100%;
            background-repeat: no-repeat;
            background-position: top center;
        }

        /*
          Monitor white boxes in source image:
          top box ~ x:165 y:185 w:172 h:33
          bottom box ~ x:165 y:231 w:182 h:36
        */
        .overlay {
            position: absolute;
            left: 16.1%;
            top: 32.1%;
            width: 18.1%;
            display: flex;
            flex-direction: column;
            gap: 13px;
        }

        .input-row {
            display: grid;
            grid-template-columns: 1fr 31px;
            gap: 7px;
            align-items: center;
        }

        .retro-input,
        .retro-output {
            height: 33px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.45);
            background: rgba(237, 247, 255, 0.26);
            color: #ffffff;
            font-family: inherit;
            font-size: clamp(6px, 0.65vw, 8px);
            letter-spacing: 0.2px;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.45),
                inset -1px -1px 0 rgba(17, 80, 115, 0.65);
            backdrop-filter: blur(1px);
        }

        .retro-input {
            width: 100%;
            padding: 0 8px;
            outline: none;
        }

        .retro-input::placeholder {
            color: rgba(242, 250, 255, 0.92);
        }

        .enter-btn {
            width: 31px;
            height: 31px;
            border-radius: 50%;
            border: 1px solid rgba(191, 236, 255, 0.95);
            background: linear-gradient(180deg, #78d5ff 0%, #3dadE6 52%, #1f87c4 100%);
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: clamp(5px, 0.5vw, 7px);
            padding: 0;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 70, 109, 0.8),
                0 2px 0 rgba(9, 70, 109, 0.65);
        }

        .enter-btn:active {
            transform: translateY(1px);
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 70, 109, 0.8),
                0 1px 0 rgba(9, 70, 109, 0.65);
        }

        .retro-output {
            width: 100%;
            height: 36px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .retro-output a {
            color: #f1fbff;
            text-decoration: none;
        }

        .retro-output a:hover { text-decoration: underline; }

        @media (max-width: 1000px) {
            .overlay {
                left: 16.6%;
                top: 32.2%;
                width: 18.8%;
            }
        }
    </style>
</head>
<body>
    <div class="scene">
        <form id="shortenerForm" class="overlay" autocomplete="off">
            <div class="input-row">
                <input id="longUrl" class="retro-input" type="url" required placeholder="https://...">
                <button class="enter-btn" type="submit">Enter</button>
            </div>
            <div id="shortResult" class="retro-output">kısa link burada görünecek</div>
        </form>
    </div>

    <script>
        (function () {
            const form = document.getElementById("shortenerForm");
            const longUrlInput = document.getElementById("longUrl");
            const shortResult = document.getElementById("shortResult");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = longUrlInput.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        shortResult.textContent = data.error || "işlem başarısız";
                        return;
                    }

                    shortResult.innerHTML =
                        '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' +
                        data.short_url +
                        "</a>";
                } catch (error) {
                    shortResult.textContent = "ağ hatası";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_bg_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    payload = request.get_json(silent=True) or {}
    long_url = (payload.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/<code>", methods=["GET"])
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)

# In-memory storage
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
EXTERNAL_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image_9.png-534c6701-9d91-4be0-a342-b05e68b65bab.png"
)


def resolve_bg_image() -> Path | None:
    candidates = [
        PROJECT_DIR / "image_9.png",
        PROJECT_DIR / "static" / "image_9.png",
        EXTERNAL_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Shortener</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background-image: url("{{ url_for('background_image') }}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            overflow: hidden;
        }

        /*
          Overlay is aligned to the monitor area in image_9.
          Keeps only the two required fields over the white boxes.
        */
        .monitor-ui {
            position: fixed;
            left: 16.7%;
            top: 35.7%;
            transform: translate(-50%, -50%);
            width: min(30vw, 300px);
            max-width: 300px;
            min-width: 220px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .input-row {
            display: grid;
            grid-template-columns: 1fr 42px;
            gap: 8px;
            align-items: center;
        }

        .retro-input,
        .retro-output {
            height: 36px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.55);
            background: rgba(232, 245, 255, 0.24);
            color: #ffffff;
            font-family: inherit;
            font-size: 8px;
            letter-spacing: 0.4px;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.35);
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.5),
                inset -1px -1px 0 rgba(18, 86, 122, 0.65);
            backdrop-filter: blur(1.2px);
        }

        .retro-input {
            width: 100%;
            padding: 0 10px;
            outline: none;
        }

        .retro-input::placeholder {
            color: rgba(241, 250, 255, 0.92);
        }

        .enter-btn {
            height: 36px;
            width: 42px;
            border-radius: 999px;
            border: 1px solid rgba(190, 235, 255, 0.95);
            background: linear-gradient(180deg, #79d6ff 0%, #3caee8 52%, #1e84c3 100%);
            color: #ffffff;
            font-family: inherit;
            font-size: 7px;
            cursor: pointer;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 71, 110, 0.8),
                0 2px 0 rgba(9, 71, 110, 0.65);
        }

        .enter-btn:active {
            transform: translateY(1px);
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(9, 71, 110, 0.8),
                0 1px 0 rgba(9, 71, 110, 0.65);
        }

        .retro-output {
            width: 100%;
            display: flex;
            align-items: center;
            padding: 0 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .retro-output a {
            color: #f2fbff;
            text-decoration: none;
        }

        .retro-output a:hover {
            text-decoration: underline;
        }

        @media (max-width: 900px) {
            .monitor-ui {
                left: 24%;
                top: 33%;
                width: min(46vw, 300px);
            }
        }
    </style>
</head>
<body>
    <form id="shortenerForm" class="monitor-ui" autocomplete="off">
        <div class="input-row">
            <input id="longUrl" class="retro-input" type="url" required placeholder="https://...">
            <button class="enter-btn" type="submit">Enter</button>
        </div>
        <div id="shortResult" class="retro-output">kısa link burada görünecek</div>
    </form>

    <script>
        (function () {
            const form = document.getElementById("shortenerForm");
            const longUrlInput = document.getElementById("longUrl");
            const shortResult = document.getElementById("shortResult");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = longUrlInput.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        shortResult.textContent = data.error || "işlem başarısız";
                        return;
                    }

                    shortResult.innerHTML = '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' + data.short_url + "</a>";
                } catch (error) {
                    shortResult.textContent = "ağ hatası";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_bg_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    payload = request.get_json(silent=True) or {}
    long_url = (payload.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/<code>", methods=["GET"])
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages

# URL storage
url_map = {}

import random
import string


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if code not in url_map:
            return code


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>URL Kısaltıcı</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root{
            --bg1: #ffe3f1;
            --bg2: #ffe9f7;
            --bg3: #f3e7ff;
            --card: rgba(255, 255, 255, 0.72);
            --card-2: rgba(255, 255, 255, 0.58);
            --border: rgba(255, 96, 196, 0.20);
            --text: #2b1430;
            --muted: rgba(43, 20, 48, 0.70);
            --primary1: #dc143c;
            --primary2: #dc143c;
            --primary3: #dc143c;
            --shadow: 0 18px 60px rgba(220, 20, 60, 0.18);
            --radius: 16px;
        }

        *{ box-sizing: border-box; }
        html, body{ height: 100%; }

        body{
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            color: var(--text);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 28px 18px;
            background:
                radial-gradient(900px 520px at 12% 18%, var(--bg1) 0%, rgba(255,227,241,0) 60%),
                radial-gradient(720px 520px at 88% 22%, var(--bg3) 0%, rgba(243,231,255,0) 60%),
                linear-gradient(180deg, var(--bg2), #ffffff);
        }

        .wrapper{
            width: min(980px, 100%);
        }

        .container{
            background: linear-gradient(180deg, var(--card), var(--card-2));
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
            padding: 26px 22px;
        }

        .topbar{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 14px;
        }

        .brand{
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .logo{
            width: 46px;
            height: 46px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary1), var(--primary3));
            box-shadow: 0 14px 30px rgba(220,20,60,0.28);
            position: relative;
        }

        .logo::after{
            content: "";
            position: absolute;
            inset: 10px;
            border-radius: 10px;
            background: rgba(255,255,255,0.35);
        }

        h1{
            margin: 0;
            font-size: 1.4rem;
            letter-spacing: -0.02em;
        }

        .subtitle{
            margin-top: 4px;
            color: var(--muted);
            font-size: 0.95rem;
        }

        .flash{
            background: rgba(255, 79, 184, 0.12);
            border: 1px solid rgba(255, 79, 184, 0.22);
            color: #a10a67;
            border-radius: 12px;
            padding: 10px 12px;
            text-align: center;
            margin-bottom: 14px;
            font-weight: 600;
        }

        .form{
            margin-top: 6px;
        }

        .form-row{
            display: flex;
            gap: 12px;
            align-items: stretch;
            flex-wrap: wrap;
        }

        input[type="url"]{
            flex: 1;
            min-width: 280px;
            padding: 12px 14px;
            border-radius: 12px;
            border: 1px solid rgba(183, 124, 255, 0.28);
            background: rgba(255,255,255,0.65);
            color: var(--text);
            outline: none;
            font-size: 1rem;
        }

        input[type="url"]::placeholder{
            color: rgba(43, 20, 48, 0.50);
        }

        input[type="url"]:focus{
            border-color: rgba(255, 79, 184, 0.55);
            box-shadow: 0 0 0 4px rgba(255,79,184,0.16);
        }

        button.primary{
            padding: 12px 16px;
            border-radius: 12px;
            border: none;
            color: #fff;
            font-weight: 750;
            font-size: 1.02rem;
            cursor: pointer;
            background: linear-gradient(135deg, var(--primary1), var(--primary3));
            box-shadow: 0 14px 30px rgba(220,20,60,0.24);
            transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
            min-width: 160px;
        }

        button.primary:hover{
            filter: brightness(1.02);
            transform: translateY(-1px);
            box-shadow: 0 18px 40px rgba(220,20,60,0.28);
        }

        button.primary:active{
            transform: translateY(0px);
        }

        .shortened-links{
            margin-top: 22px;
        }

        .shortened-links h2{
            margin: 0 0 12px 0;
            font-size: 1.05rem;
            letter-spacing: -0.01em;
        }

        .list{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .link-row{
            background: rgba(255,255,255,0.6);
            border: 1px solid rgba(255, 96, 196, 0.18);
            border-radius: 12px;
            padding: 14px 14px;
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            align-items: start;
        }

        .url-col{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .url-title{
            font-size: 0.86rem;
            font-weight: 750;
            color: rgba(43, 20, 48, 0.78);
            margin-top: 2px;
        }

        a.pill-link{
            display: inline-block;
            padding: 8px 10px;
            border-radius: 999px;
            background: rgba(255, 79, 184, 0.10);
            border: 1px solid rgba(255, 79, 184, 0.18);
            color: #8f0f5c;
            text-decoration: none;
            font-weight: 700;
            word-break: break-all;
        }

        a.pill-link:hover{
            text-decoration: underline;
        }

        a.link-inline{
            color: #6b2cff;
            text-decoration: none;
            font-weight: 650;
            word-break: break-word;
        }

        a.link-inline:hover{
            text-decoration: underline;
        }

        .row-actions{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-top: 2px;
        }

        .small-btn{
            border: 1px solid rgba(183, 124, 255, 0.25);
            background: rgba(255,255,255,0.55);
            border-radius: 12px;
            padding: 10px 12px;
            font-weight: 800;
            color: rgba(43, 20, 48, 0.85);
            cursor: pointer;
            transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
        }

        .small-btn:hover{
            background: rgba(255,255,255,0.78);
            transform: translateY(-1px);
            box-shadow: 0 12px 26px rgba(183, 124, 255, 0.16);
        }

        .small-btn.copied{
            border-color: rgba(255, 79, 184, 0.45);
            box-shadow: 0 0 0 4px rgba(255,79,184,0.14);
        }

        .footer{
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px dashed rgba(183, 124, 255, 0.25);
            color: rgba(43, 20, 48, 0.62);
            font-size: 0.92rem;
        }

        @media (max-width: 740px){
            .topbar{ flex-direction: column; align-items: flex-start; }
            .link-row{ grid-template-columns: 1fr; }
            .row-actions{ justify-content: flex-start; }
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="topbar">
                <div class="brand">
                    <div class="logo" aria-hidden="true"></div>
                    <div>
                        <h1>URL Kısaltıcı</h1>
                        <div class="subtitle">Pastel pembe, modern ve hizli</div>
                    </div>
                </div>
            </div>

            {% with messages = get_flashed_messages() %}
              {% if messages %}
                {% for msg in messages %}
                  <div class="flash" role="status">{{ msg }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}

            <form method="post" action="{{ url_for('shorten') }}" class="form">
                <div class="form-row">
                    <input type="url" name="long_url" placeholder="Kısaltmak istediğiniz URL'yi girin (örn: https://...)" required>
                    <button class="primary" type="submit">Kısalt</button>
                </div>
            </form>

            {% if url_map %}
            <section class="shortened-links">
                <h2>Kısaltılmış Linkler</h2>
                <div class="list">
                {% for code, url in url_map.items() %}
                    {% set short_url = request.url_root ~ code %}
                    <div class="link-row">
                        <div class="url-col">
                            <div class="url-title">Kısaltılmış</div>
                            <div>
                                <a class="pill-link"
                                   href="{{ url_for('redirect_short_url', code=code) }}"
                                   target="_blank"
                                   rel="noopener noreferrer">{{ short_url }}</a>
                            </div>
                            <div class="url-title">Orijinal</div>
                            <div>
                                <a class="link-inline"
                                   href="{{ url }}"
                                   target="_blank"
                                   rel="noopener noreferrer">{{ url }}</a>
                            </div>
                        </div>
                        <div class="row-actions">
                            <button type="button" class="small-btn copy-btn" data-copy="{{ short_url }}" aria-label="Kısaltılmış URL'yi kopyala">Kopyala</button>
                        </div>
                    </div>
                {% endfor %}
                </div>
            </section>
            {% endif %}

            <div class="footer">
                <span>Not: Kısaltmalar uygulama çalıştığı sürece RAM'de saklanır.</span>
            </div>
        </div>
    </div>

    <script>
        (function(){
            function copyToClipboard(text){
                if (navigator.clipboard && navigator.clipboard.writeText){
                    return navigator.clipboard.writeText(text);
                }

                // Eski tarayicilar icin basit fallback
                return new Promise(function(resolve, reject){
                    try{
                        const textarea = document.createElement('textarea');
                        textarea.value = text;
                        textarea.setAttribute('readonly', '');
                        textarea.style.position = 'absolute';
                        textarea.style.left = '-9999px';
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textarea);
                        resolve();
                    }catch(err){
                        reject(err);
                    }
                });
            }

            document.addEventListener('click', function(e){
                const btn = e.target.closest('.copy-btn');
                if(!btn) return;

                const text = btn.getAttribute('data-copy') || '';
                if(!text) return;

                copyToClipboard(text).then(function(){
                    const prev = btn.textContent;
                    btn.textContent = 'Kopyalandı';
                    btn.classList.add('copied');
                    setTimeout(function(){
                        btn.textContent = prev;
                        btn.classList.remove('copied');
                    }, 1400);
                }).catch(function(){
                    alert('Kopyalama basarisiz oldu. Linki manuel kopyalayabilirsiniz.');
                });
            });
        })();
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, url_map=url_map, request=request)


@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form.get('long_url')
    if not long_url:
        flash("Lütfen geçerli bir URL girin.")
        return redirect(url_for('index'))
    # Avoid duplicates: If exists, return same short code
    for code, url in url_map.items():
        if url == long_url:
            flash("Bu URL zaten kısaltıldı.")
            return redirect(url_for('index'))
    code = generate_short_code()
    url_map[code] = long_url
    flash(f"Kısaltılmış link oluşturuldu: {request.url_root}{code}")
    return redirect(url_for('index'))


@app.route('/<code>')
def redirect_short_url(code):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    else:
        flash("Kısaltılmış link bulunamadı.")
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
from pathlib import Path
import random
import string

from flask import Flask, jsonify, redirect, render_template_string, request, send_file, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"

# In-memory URL storage
url_map = {}

PROJECT_DIR = Path(__file__).resolve().parent
FALLBACK_IMAGE_PATH = Path(
    r"C:\Users\İnci Kaya\.cursor\projects\c-Users-nci-Kaya-OneDrive-Masa-st-URL-Kisaltici\assets\c__Users__nci_Kaya_AppData_Roaming_Cursor_User_workspaceStorage_9160d60df5b42893a1d7c7cedcdb02f9_images_image-5662b0af-b4e0-43c3-bad5-4343cbd37f03.png"
)


def resolve_background_image() -> Path | None:
    candidates = [
        PROJECT_DIR / "image_9.png",
        PROJECT_DIR / "static" / "image_9.png",
        FALLBACK_IMAGE_PATH,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if code not in url_map:
            return code


def get_or_create_code(long_url: str) -> str:
    for code, saved_url in url_map.items():
        if saved_url == long_url:
            return code
    code = generate_short_code()
    url_map[code] = long_url
    return code


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retro URL Kısaltıcı</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        html, body { width: 100%; height: 100%; margin: 0; }

        body {
            font-family: "Press Start 2P", "Courier New", monospace;
            background-image: url("{{ url_for('background_image') }}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            overflow: hidden;
            color: #e7f8ff;
        }

        .monitor-overlay {
            position: fixed;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: min(86vw, 340px);
            pointer-events: none;
        }

        .controls {
            pointer-events: auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
            margin-top: 86px;
            padding: 0 18px;
        }

        .retro-input,
        .retro-output {
            width: 100%;
            height: 34px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.45);
            background: rgba(237, 248, 255, 0.22);
            color: #ffffff;
            backdrop-filter: blur(1.2px);
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.45),
                inset -1px -1px 0 rgba(0, 56, 87, 0.65),
                0 0 0 1px rgba(12, 84, 124, 0.25);
            letter-spacing: 0.3px;
            font-family: inherit;
            font-size: 9px;
        }

        .retro-input {
            padding: 0 10px;
            outline: none;
        }

        .retro-input::placeholder {
            color: rgba(225, 243, 255, 0.88);
        }

        .retro-row {
            display: grid;
            grid-template-columns: 1fr 44px;
            gap: 8px;
            align-items: center;
        }

        .enter-btn {
            width: 44px;
            height: 34px;
            border: none;
            border-radius: 999px;
            background: linear-gradient(180deg, #78d7ff 0%, #3caee8 55%, #1f89cb 100%);
            color: #ffffff;
            cursor: pointer;
            font-family: inherit;
            font-size: 8px;
            line-height: 1;
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(8, 63, 98, 0.9),
                0 2px 0 rgba(9, 66, 98, 0.8);
        }

        .enter-btn:active {
            transform: translateY(1px);
            box-shadow:
                inset 1px 1px 0 rgba(255, 255, 255, 0.65),
                inset -1px -1px 0 rgba(8, 63, 98, 0.9),
                0 1px 0 rgba(9, 66, 98, 0.8);
        }

        .retro-output {
            display: flex;
            align-items: center;
            padding: 0 10px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .retro-output a {
            color: #eef9ff;
            text-decoration: none;
        }

        .retro-output a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="monitor-overlay">
        <form id="shortenForm" class="controls" autocomplete="off">
            <div class="retro-row">
                <input id="longUrl" class="retro-input" type="url" placeholder="https://..." required>
                <button class="enter-btn" type="submit">Enter</button>
            </div>
            <div id="shortOutput" class="retro-output">kısa link burada görünecek</div>
        </form>
    </div>

    <script>
        (function () {
            const form = document.getElementById("shortenForm");
            const input = document.getElementById("longUrl");
            const output = document.getElementById("shortOutput");

            form.addEventListener("submit", async function (event) {
                event.preventDefault();
                const longUrl = input.value.trim();
                if (!longUrl) return;

                try {
                    const response = await fetch("{{ url_for('shorten_api') }}", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ long_url: longUrl })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        output.textContent = data.error || "İşlem başarısız";
                        return;
                    }

                    output.innerHTML = '<a href="' + data.short_url + '" target="_blank" rel="noopener noreferrer">' + data.short_url + "</a>";
                } catch (error) {
                    output.textContent = "Ağ hatası oluştu";
                }
            });
        })();
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/background-image", methods=["GET"])
def background_image():
    image_path = resolve_background_image()
    if image_path is None:
        return ("image_9.png bulunamadı", 404)
    return send_file(image_path)


@app.route("/api/shorten", methods=["POST"])
def shorten_api():
    data = request.get_json(silent=True) or {}
    long_url = (data.get("long_url") or "").strip()
    if not long_url:
        return jsonify({"error": "Geçerli bir URL girin."}), 400

    code = get_or_create_code(long_url)
    short_url = f"{request.url_root}{code}"
    return jsonify({"short_url": short_url, "code": code})


@app.route("/shorten", methods=["POST"])
def shorten_form_fallback():
    long_url = (request.form.get("long_url") or "").strip()
    if not long_url:
        return redirect(url_for("index"))
    code = get_or_create_code(long_url)
    return redirect(url_for("redirect_short_url", code=code))


@app.route("/<code>")
def redirect_short_url(code: str):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages

# URL storage
url_map = {}

import random
import string


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if code not in url_map:
            return code


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>URL Kısaltıcı</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root{
            --bg1: #ffe3f1;
            --bg2: #ffe9f7;
            --bg3: #f3e7ff;
            --card: rgba(255, 255, 255, 0.72);
            --card-2: rgba(255, 255, 255, 0.58);
            --border: rgba(255, 96, 196, 0.20);
            --text: #2b1430;
            --muted: rgba(43, 20, 48, 0.70);
            --primary1: #dc143c;
            --primary2: #dc143c;
            --primary3: #dc143c;
            --shadow: 0 18px 60px rgba(220, 20, 60, 0.18);
            --radius: 16px;
        }

        *{ box-sizing: border-box; }
        html, body{ height: 100%; }

        body{
            margin: 0;
            font-family: "Segoe UI", Arial, sans-serif;
            color: var(--text);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 28px 18px;
            background:
                radial-gradient(900px 520px at 12% 18%, var(--bg1) 0%, rgba(255,227,241,0) 60%),
                radial-gradient(720px 520px at 88% 22%, var(--bg3) 0%, rgba(243,231,255,0) 60%),
                linear-gradient(180deg, var(--bg2), #ffffff);
        }

        .wrapper{
            width: min(980px, 100%);
        }

        .container{
            background: linear-gradient(180deg, var(--card), var(--card-2));
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            backdrop-filter: blur(10px);
            padding: 26px 22px;
        }

        .topbar{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 14px;
        }

        .brand{
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .logo{
            width: 46px;
            height: 46px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary1), var(--primary3));
            box-shadow: 0 14px 30px rgba(220,20,60,0.28);
            position: relative;
        }

        .logo::after{
            content: "";
            position: absolute;
            inset: 10px;
            border-radius: 10px;
            background: rgba(255,255,255,0.35);
        }

        h1{
            margin: 0;
            font-size: 1.4rem;
            letter-spacing: -0.02em;
        }

        .subtitle{
            margin-top: 4px;
            color: var(--muted);
            font-size: 0.95rem;
        }

        .flash{
            background: rgba(255, 79, 184, 0.12);
            border: 1px solid rgba(255, 79, 184, 0.22);
            color: #a10a67;
            border-radius: 12px;
            padding: 10px 12px;
            text-align: center;
            margin-bottom: 14px;
            font-weight: 600;
        }

        .form{
            margin-top: 6px;
        }

        .form-row{
            display: flex;
            gap: 12px;
            align-items: stretch;
            flex-wrap: wrap;
        }

        input[type="url"]{
            flex: 1;
            min-width: 280px;
            padding: 12px 14px;
            border-radius: 12px;
            border: 1px solid rgba(183, 124, 255, 0.28);
            background: rgba(255,255,255,0.65);
            color: var(--text);
            outline: none;
            font-size: 1rem;
        }

        input[type="url"]::placeholder{
            color: rgba(43, 20, 48, 0.50);
        }

        input[type="url"]:focus{
            border-color: rgba(255, 79, 184, 0.55);
            box-shadow: 0 0 0 4px rgba(255,79,184,0.16);
        }

        button.primary{
            padding: 12px 16px;
            border-radius: 12px;
            border: none;
            color: #fff;
            font-weight: 750;
            font-size: 1.02rem;
            cursor: pointer;
            background: linear-gradient(135deg, var(--primary1), var(--primary3));
            box-shadow: 0 14px 30px rgba(220,20,60,0.24);
            transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.12s ease;
            min-width: 160px;
        }

        button.primary:hover{
            filter: brightness(1.02);
            transform: translateY(-1px);
            box-shadow: 0 18px 40px rgba(220,20,60,0.28);
        }

        button.primary:active{
            transform: translateY(0px);
        }

        .shortened-links{
            margin-top: 22px;
        }

        .shortened-links h2{
            margin: 0 0 12px 0;
            font-size: 1.05rem;
            letter-spacing: -0.01em;
        }

        .list{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .link-row{
            background: rgba(255,255,255,0.6);
            border: 1px solid rgba(255, 96, 196, 0.18);
            border-radius: 12px;
            padding: 14px 14px;
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 12px;
            align-items: start;
        }

        .url-col{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .url-title{
            font-size: 0.86rem;
            font-weight: 750;
            color: rgba(43, 20, 48, 0.78);
            margin-top: 2px;
        }

        a.pill-link{
            display: inline-block;
            padding: 8px 10px;
            border-radius: 999px;
            background: rgba(255, 79, 184, 0.10);
            border: 1px solid rgba(255, 79, 184, 0.18);
            color: #8f0f5c;
            text-decoration: none;
            font-weight: 700;
            word-break: break-all;
        }

        a.pill-link:hover{
            text-decoration: underline;
        }

        a.link-inline{
            color: #6b2cff;
            text-decoration: none;
            font-weight: 650;
            word-break: break-word;
        }

        a.link-inline:hover{
            text-decoration: underline;
        }

        .row-actions{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-top: 2px;
        }

        .small-btn{
            border: 1px solid rgba(183, 124, 255, 0.25);
            background: rgba(255,255,255,0.55);
            border-radius: 12px;
            padding: 10px 12px;
            font-weight: 800;
            color: rgba(43, 20, 48, 0.85);
            cursor: pointer;
            transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
        }

        .small-btn:hover{
            background: rgba(255,255,255,0.78);
            transform: translateY(-1px);
            box-shadow: 0 12px 26px rgba(183, 124, 255, 0.16);
        }

        .small-btn.copied{
            border-color: rgba(255, 79, 184, 0.45);
            box-shadow: 0 0 0 4px rgba(255,79,184,0.14);
        }

        .footer{
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px dashed rgba(183, 124, 255, 0.25);
            color: rgba(43, 20, 48, 0.62);
            font-size: 0.92rem;
        }

        @media (max-width: 740px){
            .topbar{ flex-direction: column; align-items: flex-start; }
            .link-row{ grid-template-columns: 1fr; }
            .row-actions{ justify-content: flex-start; }
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            <div class="topbar">
                <div class="brand">
                    <div class="logo" aria-hidden="true"></div>
                    <div>
                        <h1>URL Kısaltıcı</h1>
                        <div class="subtitle">Pastel pembe, modern ve hizli</div>
                    </div>
                </div>
            </div>

            {% with messages = get_flashed_messages() %}
              {% if messages %}
                {% for msg in messages %}
                  <div class="flash" role="status">{{ msg }}</div>
                {% endfor %}
              {% endif %}
            {% endwith %}

            <form method="post" action="{{ url_for('shorten') }}" class="form">
                <div class="form-row">
                    <input type="url" name="long_url" placeholder="Kısaltmak istediğiniz URL'yi girin (örn: https://...)" required>
                    <button class="primary" type="submit">Kısalt</button>
                </div>
            </form>

            {% if url_map %}
            <section class="shortened-links">
                <h2>Kısaltılmış Linkler</h2>
                <div class="list">
                {% for code, url in url_map.items() %}
                    {% set short_url = request.url_root ~ code %}
                    <div class="link-row">
                        <div class="url-col">
                            <div class="url-title">Kısaltılmış</div>
                            <div>
                                <a class="pill-link"
                                   href="{{ url_for('redirect_short_url', code=code) }}"
                                   target="_blank"
                                   rel="noopener noreferrer">{{ short_url }}</a>
                            </div>
                            <div class="url-title">Orijinal</div>
                            <div>
                                <a class="link-inline"
                                   href="{{ url }}"
                                   target="_blank"
                                   rel="noopener noreferrer">{{ url }}</a>
                            </div>
                        </div>
                        <div class="row-actions">
                            <button type="button" class="small-btn copy-btn" data-copy="{{ short_url }}" aria-label="Kısaltılmış URL'yi kopyala">Kopyala</button>
                        </div>
                    </div>
                {% endfor %}
                </div>
            </section>
            {% endif %}

            <div class="footer">
                <span>Not: Kısaltmalar uygulama çalıştığı sürece RAM'de saklanır.</span>
            </div>
        </div>
    </div>

    <script>
        (function(){
            function copyToClipboard(text){
                if (navigator.clipboard && navigator.clipboard.writeText){
                    return navigator.clipboard.writeText(text);
                }

                // Eski tarayicilar icin basit fallback
                return new Promise(function(resolve, reject){
                    try{
                        const textarea = document.createElement('textarea');
                        textarea.value = text;
                        textarea.setAttribute('readonly', '');
                        textarea.style.position = 'absolute';
                        textarea.style.left = '-9999px';
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textarea);
                        resolve();
                    }catch(err){
                        reject(err);
                    }
                });
            }

            document.addEventListener('click', function(e){
                const btn = e.target.closest('.copy-btn');
                if(!btn) return;

                const text = btn.getAttribute('data-copy') || '';
                if(!text) return;

                copyToClipboard(text).then(function(){
                    const prev = btn.textContent;
                    btn.textContent = 'Kopyalandı';
                    btn.classList.add('copied');
                    setTimeout(function(){
                        btn.textContent = prev;
                        btn.classList.remove('copied');
                    }, 1400);
                }).catch(function(){
                    alert('Kopyalama basarisiz oldu. Linki manuel kopyalayabilirsiniz.');
                });
            });
        })();
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, url_map=url_map, request=request)


@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form.get('long_url')
    if not long_url:
        flash("Lütfen geçerli bir URL girin.")
        return redirect(url_for('index'))
    # Avoid duplicates: If exists, return same short code
    for code, url in url_map.items():
        if url == long_url:
            flash("Bu URL zaten kısaltıldı.")
            return redirect(url_for('index'))
    code = generate_short_code()
    url_map[code] = long_url
    flash(f"Kısaltılmış link oluşturuldu: {request.url_root}{code}")
    return redirect(url_for('index'))


@app.route('/<code>')
def redirect_short_url(code):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    else:
        flash("Kısaltılmış link bulunamadı.")
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages

# URL storage
url_map = {}

import random
import string

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if code not in url_map:
            return code

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>URL Kısaltıcı</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        html, body { height: 100%; }

        body{
            margin: 0;
            font-family: "Courier New", "Lucida Console", monospace;
            color: #1c1c1c;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            background:
                radial-gradient(circle at 18% 20%, rgba(255,255,255,0.25), rgba(255,255,255,0) 45%),
                radial-gradient(circle at 82% 80%, rgba(255,255,255,0.18), rgba(255,255,255,0) 42%),
                linear-gradient(180deg, #4f91d6 0%, #3a7ec3 55%, #346fab 100%);
        }

        .stage{
            width: min(760px, 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        }

        .monitor{
            width: min(560px, 100%);
            padding: 18px;
            border-radius: 8px;
            background: #d9d0bf;
            border-top: 4px solid #efeadf;
            border-left: 4px solid #e8e1d3;
            border-right: 4px solid #9f9687;
            border-bottom: 4px solid #8f8678;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.25);
        }

        .screen-bevel{
            background: #c8bfaf;
            border-top: 3px solid #f2ece2;
            border-left: 3px solid #ebe4d8;
            border-right: 3px solid #9a9183;
            border-bottom: 3px solid #8c8376;
            padding: 12px;
        }

        .screen{
            border-radius: 3px;
            padding: 18px 16px 16px;
            min-height: 230px;
            background:
                linear-gradient(180deg, #2ec2ee 0%, #14a7d9 55%, #0e94c2 100%);
            border-top: 2px solid rgba(255,255,255,0.55);
            border-left: 2px solid rgba(255,255,255,0.42);
            border-right: 2px solid rgba(12, 85, 117, 0.8);
            border-bottom: 2px solid rgba(8, 66, 92, 0.85);
            box-shadow: inset 0 0 0 1px rgba(0, 38, 56, 0.35);
        }

        .logo-area{
            width: 150px;
            height: 110px;
            margin: 0 auto 16px;
            display: grid;
            place-items: center;
            color: #ffffff;
            font-size: 1rem;
            letter-spacing: 1px;
            background: linear-gradient(180deg, rgba(255,255,255,0.30), rgba(255,255,255,0.10));
            border-top: 2px solid rgba(255,255,255,0.72);
            border-left: 2px solid rgba(255,255,255,0.60);
            border-right: 2px solid rgba(9, 88, 124, 0.72);
            border-bottom: 2px solid rgba(8, 77, 107, 0.75);
            border-radius: 8px;
            text-shadow: 0 1px 1px rgba(0,0,0,0.25);
        }

        .flash{
            margin: 0 auto 12px;
            width: min(380px, 100%);
            background: #ffe5ea;
            color: #78212f;
            border-top: 2px solid #fff6f8;
            border-left: 2px solid #fff0f3;
            border-right: 2px solid #c08d98;
            border-bottom: 2px solid #ac7a85;
            padding: 8px 10px;
            font-size: 0.86rem;
            text-align: center;
        }

        .input-row{
            width: min(430px, 100%);
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 54px;
            gap: 8px;
            align-items: center;
        }

        input[type="url"]{
            width: 100%;
            height: 42px;
            padding: 10px 12px;
            font-family: inherit;
            font-size: 0.95rem;
            color: #1c2c35;
            background: #f8f8f8;
            border: none;
            border-top: 2px solid #7ba0b1;
            border-left: 2px solid #7ba0b1;
            border-right: 2px solid #f7fdff;
            border-bottom: 2px solid #f7fdff;
            outline: none;
        }

        input[type="url"]::placeholder{
            color: #6e7f88;
        }

        .enter-btn{
            width: 46px;
            height: 46px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.76rem;
            font-weight: 700;
            color: #ffffff;
            background: linear-gradient(180deg, #6ecfff 0%, #2f9fe1 55%, #1f86c5 100%);
            border-top: 2px solid #c2ecff;
            border-left: 2px solid #b5e6ff;
            border-right: 2px solid #0f5f91;
            border-bottom: 2px solid #0a4f78;
            box-shadow: 0 2px 0 rgba(9, 66, 98, 0.65);
        }

        .enter-btn:active{
            transform: translateY(1px);
            box-shadow: 0 1px 0 rgba(9, 66, 98, 0.65);
        }

        .results{
            width: min(560px, 100%);
            background: rgba(236, 231, 220, 0.95);
            padding: 12px;
            border-top: 3px solid #f1ece1;
            border-left: 3px solid #ece5d8;
            border-right: 3px solid #9e9688;
            border-bottom: 3px solid #8e8578;
            color: #2d2a25;
            font-size: 0.84rem;
        }

        .results-title{
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: 0.6px;
        }

        .row{
            padding: 6px 8px;
            margin-bottom: 6px;
            background: #f4f4f2;
            border-top: 1px solid #ffffff;
            border-left: 1px solid #ffffff;
            border-right: 1px solid #b7b7b1;
            border-bottom: 1px solid #b7b7b1;
            word-break: break-all;
        }

        .row a{
            color: #194f7e;
            text-decoration: none;
        }

        .row a:hover{
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="stage">
        <section class="monitor">
            <div class="screen-bevel">
                <div class="screen">
                    <div class="logo-area">[Logo Alanı]</div>

                    {% with messages = get_flashed_messages() %}
                      {% if messages %}
                        {% for msg in messages %}
                          <div class="flash" role="status">{{ msg }}</div>
                        {% endfor %}
                      {% endif %}
                    {% endwith %}

                    <form method="post" action="{{ url_for('shorten') }}">
                        <div class="input-row">
                            <input type="url" name="long_url" placeholder="https://ornek.com/uzun-link" required>
                            <button class="enter-btn" type="submit">Enter</button>
                        </div>
                    </form>
                </div>
            </div>
        </section>

        {% if url_map %}
        <section class="results">
            <div class="results-title">KISALTILMIS LINKLER</div>
            {% for code, url in url_map.items() %}
                <div class="row">
                    <a href="{{ url_for('redirect_short_url', code=code) }}" target="_blank" rel="noopener noreferrer">{{ request.url_root ~ code }}</a>
                    -> {{ url }}
                </div>
            {% endfor %}
        </section>
        {% endif %}

        <div class="results">
            <div class="row">Not: Kısaltmalar uygulama çalıştığı sürece RAM'de saklanır.</div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, url_map=url_map, request=request)

@app.route('/shorten', methods=['POST'])
def shorten():
    long_url = request.form.get('long_url')
    if not long_url:
        flash("Lütfen geçerli bir URL girin.")
        return redirect(url_for('index'))
    # Avoid duplicates: If exists, return same short code
    for code, url in url_map.items():
        if url == long_url:
            flash("Bu URL zaten kısaltıldı.")
            return redirect(url_for('index'))
    code = generate_short_code()
    url_map[code] = long_url
    flash(f"Kısaltılmış link oluşturuldu: {request.url_root}{code}")
    return redirect(url_for('index'))

@app.route('/<code>')
def redirect_short_url(code):
    long_url = url_map.get(code)
    if long_url:
        return redirect(long_url)
    else:
        flash("Kısaltılmış link bulunamadı.")
        return redirect(url_for('index'))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
