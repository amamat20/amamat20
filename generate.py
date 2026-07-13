from PIL import Image, ImageEnhance, ImageOps
from xml.sax.saxutils import escape

import os
import requests


ASCII_CHARS = (
    "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/"
    "\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
)


# =========================
# GITHUB CONFIGURATION
# =========================

GITHUB_USERNAME = "amamat20"

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN"
)


GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


if GITHUB_TOKEN:

    GITHUB_HEADERS[
        "Authorization"
    ] = f"Bearer {GITHUB_TOKEN}"


# =========================
# GITHUB API CLIENT
# =========================

def github_get(
    url,
    params=None
):

    response = requests.get(
        url,
        headers=GITHUB_HEADERS,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response

def print_rate_limit():

    response = github_get(
        "https://api.github.com/rate_limit"
    )

    data = response.json()

    core = data["resources"]["core"]

    print(
        "GitHub Rate Limit:"
    )

    print(
        "Limit:",
        core["limit"]
    )

    print(
        "Remaining:",
        core["remaining"]
    )

    print(
        "Used:",
        core["used"]
    )

# =========================
# GITHUB PROFILE
# =========================

def get_github_profile(
    username
):

    url = (
        f"https://api.github.com/users/"
        f"{username}"
    )

    response = github_get(
        url
    )

    data = response.json()

    return {
        "login": data["login"],
        "name": data["name"],
        "public_repos": data["public_repos"],
        "followers": data["followers"],
        "following": data["following"],
    }


# =========================
# GITHUB REPOSITORIES
# =========================

def get_github_repositories(
    username
):

    url = (
        f"https://api.github.com/users/"
        f"{username}/repos"
    )

    params = {
        "per_page": 100,
        "sort": "updated"
    }

    response = github_get(
        url,
        params=params
    )

    return response.json()


# =========================
# REPOSITORY LANGUAGES
# =========================

def get_repository_languages(
    username,
    repository_name
):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/"
        f"{repository_name}/languages"
    )

    response = github_get(
        url
    )

    return response.json()


# =========================
# REPOSITORY COMMITS
# =========================

def get_repository_commit_count(
    username,
    repository_name,
    author
):

    url = (
        f"https://api.github.com/repos/"
        f"{username}/"
        f"{repository_name}/commits"
    )

    page = 1

    commit_count = 0


    while True:

        params = {
            "author": author,
            "per_page": 100,
            "page": page
        }


        response = github_get(
            url,
            params=params
        )


        commits = response.json()


        commit_count += len(
            commits
        )


        if len(commits) < 100:

            break


        page += 1


    return commit_count


# =========================
# CHECK AUTHENTICATION
# =========================

if GITHUB_TOKEN:

    print(
        "GitHub API: authenticated"
    )

else:

    print(
        "GitHub API: unauthenticated"
    )
    
    print_rate_limit()
    
    
# =========================
# FETCH GITHUB DATA
# =========================

github_profile = get_github_profile(
    GITHUB_USERNAME
)


github_repositories = get_github_repositories(
    GITHUB_USERNAME
)


print(
    "GitHub profile:",
    github_profile
)


# =========================
# TOTAL STARS
# =========================

total_stars = sum(
    repository["stargazers_count"]
    for repository in github_repositories
)


# =========================
# LANGUAGE STATISTICS
# =========================

language_bytes = {}


for repository in github_repositories:

    repository_name = repository["name"]

    repository_languages = (
        get_repository_languages(
            GITHUB_USERNAME,
            repository_name
        )
    )

    for language, byte_count in (
        repository_languages.items()
    ):

        language_bytes[language] = (
            language_bytes.get(
                language,
                0
            )
            + byte_count
        )


total_language_bytes = sum(
    language_bytes.values()
)


language_percentages = []


if total_language_bytes > 0:

    for language, byte_count in (
        language_bytes.items()
    ):

        percentage = (
            byte_count
            / total_language_bytes
            * 100
        )

        language_percentages.append(
            (
                language,
                percentage
            )
        )


language_percentages.sort(
    key=lambda item: item[1],
    reverse=True
)


top_languages = (
    language_percentages[:3]
)


top_languages_text = ", ".join(
    f"{language} {percentage:.1f}%"
    for language, percentage
    in top_languages
)


# =========================
# COMMIT STATISTICS
# =========================

total_commits = 0


for repository in github_repositories:

    repository_name = repository["name"]


    repository_commit_count = (
        get_repository_commit_count(
            GITHUB_USERNAME,
            repository_name,
            GITHUB_USERNAME
        )
    )


    total_commits += (
        repository_commit_count
    )


    print(
        repository_name,
        "→",
        repository_commit_count,
        "commits"
    )


# =========================
# DEBUG OUTPUT
# =========================

print(
    "Total repositories:",
    len(github_repositories)
)

print(
    "Total stars:",
    total_stars
)

print(
    "Language bytes:",
    language_bytes
)

print(
    "Top languages:",
    top_languages_text
)

print(
    "Total commits:",
    total_commits
)

# =========================
# IMAGE PROCESSING
# =========================

image = Image.open("assets/profile.jpg")

image = ImageOps.exif_transpose(image)

image = image.convert("RGB")


# =========================
# CROP
# =========================

width_original, height_original = image.size

crop_height = int(height_original * 0.72)

image = image.crop(
    (
        0,
        0,
        width_original,
        crop_height
    )
)


# =========================
# BACKGROUND MASK
# =========================

rgb_pixels = list(image.getdata())

foreground_mask = []


for red, green, blue in rgb_pixels:

    is_blue_background = (
        blue > 120
        and blue > red * 1.5
        and blue > green * 1.3
    )

    foreground_mask.append(
        not is_blue_background
    )


# =========================
# GRAYSCALE
# =========================

grayscale_image = image.convert("L")

grayscale_image = ImageEnhance.Contrast(
    grayscale_image
).enhance(1.6)


# =========================
# ASCII SIZE
# =========================

ascii_width = 50

aspect_ratio = (
    grayscale_image.height
    / grayscale_image.width
)

ascii_height = int(
    ascii_width
    * aspect_ratio
    * 0.45
)


grayscale_image = grayscale_image.resize(
    (
        ascii_width,
        ascii_height
    )
)


# Resize mask
mask_image = Image.new(
    "L",
    image.size
)


mask_pixels = [
    255 if foreground else 0
    for foreground in foreground_mask
]


mask_image.putdata(mask_pixels)


mask_image = mask_image.resize(
    (
        ascii_width,
        ascii_height
    )
)


# =========================
# ASCII GENERATION
# =========================

pixels = list(
    grayscale_image.getdata()
)

mask = list(
    mask_image.getdata()
)


ascii_lines = []

current_line = ""


for index, pixel in enumerate(pixels):

    # Background menjadi spasi
    if mask[index] < 128:

        character = " "

    else:

        char_index = (
            pixel
            * (len(ASCII_CHARS) - 1)
            // 255
        )

        character = ASCII_CHARS[
            char_index
        ]


    current_line += character


    if (index + 1) % ascii_width == 0:

        ascii_lines.append(
            current_line
        )

        current_line = ""


# =========================
# TERMINAL PREVIEW
# =========================

for line in ascii_lines:

    print(line)


# =========================
# SVG CONFIGURATION
# =========================

SVG_WIDTH = 1000
SVG_HEIGHT = 680

BACKGROUND = "#0d1117"

TEXT_COLOR = "#c9d1d9"

ASCII_X = 35
ASCII_Y = 45

FONT_SIZE = 10

LINE_HEIGHT = 11


# =========================
# SVG CONFIGURATION
# =========================

SVG_WIDTH = 1000
SVG_HEIGHT = 680

BACKGROUND = "#0d1117"
TEXT_COLOR = "#c9d1d9"

BLUE = "#58a6ff"
ORANGE = "#d29922"
GREEN = "#3fb950"
PURPLE = "#bc8cff"
RED = "#f85149"


# ASCII POSITION

ASCII_X = 35
ASCII_Y = 45

ASCII_FONT_SIZE = 10
ASCII_LINE_HEIGHT = 11


# PROFILE POSITION

PROFILE_X = 430
PROFILE_Y = 55

PROFILE_FONT_SIZE = 14
PROFILE_LINE_HEIGHT = 24


# =========================
# PROFILE DATA
# =========================

profile_lines = [
    {
        "type": "header",
        "text": "bayuputra"
    },
    {
        "type": "separator",
        "text": "----------------------------------------"
    },
    {
        "type": "empty"
    },
    {
        "type": "info",
        "label": "OS",
        "value": "Windows 11",
        "color": BLUE
    },
    {
        "type": "info",
        "label": "Education",
        "value": "Polman Bandung",
        "color": ORANGE
    },
    {
        "type": "info",
        "label": "Major",
        "value": "Industrial Informatics",
        "color": GREEN
    },
    {
        "type": "empty"
    },
    {
        "type": "section",
        "text": "Languages.Programming",
        "color": ORANGE
    },
    {
        "type": "value",
        "text": "Python, JavaScript"
    },
    {
        "type": "value",
        "text": "Kotlin, PHP"
    },
    {
        "type": "empty"
    },
    {
        "type": "section",
        "text": "Backend",
        "color": PURPLE
    },
    {
        "type": "value",
        "text": "FastAPI, Django"
    },
    {
        "type": "value",
        "text": "Node.js, Laravel"
    },
    {
        "type": "empty"
    },
    {
        "type": "section",
        "text": "Interests",
        "color": GREEN
    },
    {
        "type": "value",
        "text": "Backend Systems"
    },
    {
        "type": "value",
        "text": "Machine Learning"
    },
    {
        "type": "value",
        "text": "AI Engineering"
    },
        {
        "type": "empty"
    },
    {
        "type": "section",
        "text": "GitHub Stats",
        "color": BLUE
    },
    {
        "type": "info",
        "label": "Repos",
        "value": str(
            github_profile["public_repos"]
        ),
        "color": BLUE
    },
    {
        "type": "info",
        "label": "Followers",
        "value": str(
            github_profile["followers"]
        ),
        "color": PURPLE
    },
    {
        "type": "info",
        "label": "Following",
        "value": str(
            github_profile["following"]
        ),
        "color": GREEN
    },
    {
    "type": "info",
    "label": "Total Stars",
    "value": str(
        total_stars
    ),
    "color": ORANGE
},
    {
    "type": "info",
    "label": "Total Commits",
    "value": str(
        total_commits
    ),
    "color": PURPLE
},
{
    "type": "info",
    "label": "Top Languages",
    "value": top_languages_text,
    "color": GREEN
},
]


# =========================
# SVG GENERATION
# =========================

svg = f"""
<svg
    width="{SVG_WIDTH}"
    height="{SVG_HEIGHT}"
    viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}"
    xmlns="http://www.w3.org/2000/svg"
>

<rect
    width="100%"
    height="100%"
    rx="12"
    fill="{BACKGROUND}"
/>


<!-- ASCII ART -->

<g
    font-family="monospace"
    font-size="{ASCII_FONT_SIZE}px"
    fill="{TEXT_COLOR}"
>
"""


# =========================
# ASCII SVG
# =========================

for line_number, line in enumerate(
    ascii_lines
):

    y = (
        ASCII_Y
        + line_number
        * ASCII_LINE_HEIGHT
    )

    safe_line = escape(line)

    svg += f"""
    <text
        x="{ASCII_X}"
        y="{y}"
        xml:space="preserve"
    >{safe_line}</text>
    """


svg += """
</g>


<!-- PROFILE INFORMATION -->

"""


# =========================
# PROFILE SVG
# =========================

LABEL_WIDTH = 24


for line_number, line in enumerate(profile_lines):

    y = (
        PROFILE_Y
        + line_number
        * PROFILE_LINE_HEIGHT
    )

    line_type = line["type"]


    # =====================
    # EMPTY LINE
    # =====================

    if line_type == "empty":
        continue


    # =====================
    # HEADER
    # =====================

    if line_type == "header":

        safe_text = escape(
            line["text"]
        )

        svg += f"""
        <text
            x="{PROFILE_X}"
            y="{y}"
            fill="{TEXT_COLOR}"
            font-family="monospace"
            font-size="{PROFILE_FONT_SIZE}px"
            font-weight="bold"
        >{safe_text}</text>
        """


    # =====================
    # SEPARATOR
    # =====================

    elif line_type == "separator":

        safe_text = escape(
            line["text"]
        )

        svg += f"""
        <text
            x="{PROFILE_X}"
            y="{y}"
            fill="{TEXT_COLOR}"
            font-family="monospace"
            font-size="{PROFILE_FONT_SIZE}px"
        >{safe_text}</text>
        """


    # =====================
    # INFO
    # =====================

    elif line_type == "info":

        label = line["label"]
        value = line["value"]
        color = line["color"]

        label_text = f"{label}:"

        dots_count = (
            LABEL_WIDTH
            - len(label_text)
        )

        dots = "." * dots_count

        safe_label = escape(
            label_text
        )

        safe_dots = escape(
            dots
        )

        safe_value = escape(
            value
        )

        svg += f"""
        <text
            x="{PROFILE_X}"
            y="{y}"
            font-family="monospace"
            font-size="{PROFILE_FONT_SIZE}px"
            xml:space="preserve"
        >
            <tspan
                fill="{color}"
                font-weight="bold"
            >{safe_label}</tspan>

            <tspan
                fill="#6e7681"
            > {safe_dots} </tspan>

            <tspan
                fill="{TEXT_COLOR}"
            >{safe_value}</tspan>

        </text>
        """


    # =====================
    # SECTION
    # =====================

    elif line_type == "section":

        safe_text = escape(
            line["text"]
        )

        color = line["color"]

        svg += f"""
        <text
            x="{PROFILE_X}"
            y="{y}"
            fill="{color}"
            font-family="monospace"
            font-size="{PROFILE_FONT_SIZE}px"
            font-weight="bold"
        >{safe_text}:</text>
        """


    # =====================
    # VALUE
    # =====================

    elif line_type == "value":

        safe_text = escape(
            line["text"]
        )

        dots = "." * LABEL_WIDTH

        svg += f"""
        <text
            x="{PROFILE_X}"
            y="{y}"
            font-family="monospace"
            font-size="{PROFILE_FONT_SIZE}px"
            xml:space="preserve"
        >

            <tspan
                fill="#6e7681"
            >{dots} </tspan>

            <tspan
                fill="{TEXT_COLOR}"
            >{safe_text}</tspan>

        </text>
        """


svg += """

</svg>
"""


# =========================
# SAVE SVG
# =========================

with open(
    "profile.svg",
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print(
    "\nprofile.svg berhasil dibuat"
)