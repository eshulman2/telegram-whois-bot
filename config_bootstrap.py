
import hashlib
import getpass
import json
import os

def compare_passwords():
        password = getpass.getpass(prompt="please enter the password"
                            " you would like users to idetify with: ",
                            stream=None)
        password2 = getpass.getpass(prompt="please re-enter the password", 
                                    stream=None)
        
        return password, (password2 == password)


def main():
    if "BOT_PASSWORD" in os.environ:
        password = os.environ["BOT_PASSWORD"]
    else:
        try:
            eq = False
            while not eq:
                password, eq = compare_passwords()
                if eq is False:
                    print("passwords doesn't match")

        except Exception as e:
            raise RuntimeError
    
    if "BOT_TOKEN" in os.environ:
        token = os.environ["BOT_TOKEN"]
    else:
        token = input("please enter the token yourecived from BotFather: ")
    
    password_hash = hashlib.sha512(password.encode("utf-8")).hexdigest()

    configuration = {"token": token, "password": password_hash}

    with open("./config.json", "w") as config:
        config.write(json.dumps(configuration, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()
