from flask import Flask, render_template, request, url_for
import requests as req
from openai import OpenAI
from enum import Enum
import os

app = Flask(__name__, template_folder="templates")

app_url = f"https://0b50-2405-201-2003-b884-a0d5-2e07-f8a9-a77a.ngrok-free.app"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINATA_API_KEY = os.environ.get("PINATA_API_KEY")
client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)


class CharName(Enum):
    PHOEBE = "Phoebe"
    JOEY = "Joey"
    CHANDLER = "Chandler"
    ROSS = "Ross"
    MONICA = "Monica"
    RACHAEL = "Rachael"


def get_character_image(char_name):
    # return "https://res.cloudinary.com/drlni3r6u/image/upload/c_fit,h_360,w_360/warpcast-friends/ouuhunnstpsondtk2lcj.jpg"
    match char_name:
        case CharName.PHOEBE:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138533/warpcast-friends/trvjhry6zvnfrawsr5ro.jpg"
        case CharName.JOEY:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138529/warpcast-friends/dhtbq7musjx74ewur09y.jpg"
        case CharName.CHANDLER:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138541/warpcast-friends/aqokrm6eusld5l3i6ats.jpg"
        case CharName.ROSS:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138535/warpcast-friends/ae8x49bdcm9narckoiqc.jpg"
        case CharName.MONICA:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138538/warpcast-friends/aug9vinkihn0gvlvtqvz.jpg"
        case CharName.RACHAEL:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138510/warpcast-friends/ouuhunnstpsondtk2lcj.jpg"
        case _:
            return "https://res.cloudinary.com/drlni3r6u/image/upload/v1711138529/warpcast-friends/dhtbq7musjx74ewur09y.jpg"


def get_result(statements):
    PROMPT_TEMPLATE = f"""
  The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.  

  You are supposed to help me identify which FRIENDS series character does the following lines look like ?
  You are allowed to only answer the following characters: 
  1. Chandler
  2. Joey
  3. Phoebe
  4. Ross
  5. Monica
  6. Rachael

  Please make sure that your answer should be in the following format
  "Following Casts are of:<Character Name>"

  Statements: {statements}
  """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion


@app.route("/")
def index():
    print("here")

    image_url = f"https://res.cloudinary.com/drlni3r6u/image/upload/v1711225941/warpcast-friends/ruyp2oj5xew4fg4dqynv.jpg"
    print(image_url)
    post_url = f"{app_url}/action"
    return render_template("firstTemplate.html", image_url=image_url, post_url=post_url)


@app.route("/action", methods=["POST"])
def action():
    data = request.get_json(silent=True)
    untrusted_data = data["untrustedData"]
    fid = untrusted_data["fid"]
    url = f"https://api.pinata.cloud/v3/farcaster/casts?fid={fid}"

    token = PINATA_API_KEY

    headers = {"Authorization": f"Bearer {token}"}

    response = req.get(url, headers=headers)

    if response.status_code == 200:
        # Success!
        res = response.json()
        casts_obj = res["data"]["casts"]
        user_casts = [cast["content"] for cast in casts_obj]

        # print(f"API call successful. Response: {user_casts}")
        user_cast_statements = "\n".join(user_casts)
        res = get_result(user_cast_statements)
        char_name = res.choices[0].message.content.split(":")[1]
        if char_name not in [char.value for char in CharName]:
            char_name = CharName.PHOEBE.value

        char_name_obj = CharName(char_name.strip())
        image_url = get_character_image(char_name_obj)
        # return res.choices[0].text
    else:
        # Error handling
        print(f"API call failed. Status code: {response.status_code}")
        print(f"Error message: {response.text}")

    # TODO : set from model response
    print(render_template("secondTemplate.html", image_url=image_url))
    return render_template("secondTemplate.html", image_url=image_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
