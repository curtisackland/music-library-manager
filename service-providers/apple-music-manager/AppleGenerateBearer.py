import json
import jwt
import datetime

CONFIG_FILE = "secrets/config.json"

def getConfig():
    with open(CONFIG_FILE, "r") as inConfigFile:
        return json.load(inConfigFile)

def getPrivateKey() -> str:
    with open(getConfig()["privateKeyFile"], "r") as inKeyFile:
        return inKeyFile.read()

def generateNewDeveloperBearer():
    headers = {
        "kid":getConfig()["kid"]
    }
    iat = datetime.datetime.now().timestamp()
    body = {
        "iss": getConfig()["iss"],
        "iat": iat,
        "exp": iat + 2592000, # 1 month
    }

    privateKey = getPrivateKey()
    bearer = jwt.encode(body, headers=headers, key=privateKey, algorithm="ES256")

    bearerJson = {
        "bearer":bearer,
        "exp":iat + 2592000,
    }

    with open(getConfig()["bearerCache"], "w") as outBearerFile:
        json.dump(bearerJson, outBearerFile)

    return bearerJson


if __name__ == "__main__":
    generateNewDeveloperBearer()
