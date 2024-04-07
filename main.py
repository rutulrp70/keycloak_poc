import requests, json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from keycloak import KeycloakOpenID
# from keycloak import KeycloakAdmin
# from keycloak import KeycloakOpenIDConnection

def get_application():
    app = FastAPI()

    origins = ['*']

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = get_application()


# keycloak_connection = KeycloakOpenIDConnection(
#                         server_url="http://0.0.0.0:8080/",
#                         username='rutulrp70',
#                         password='rutul',
#                         realm_name="master",
#                         user_realm_name="myrealm",
#                         client_id="myclient",
#                         client_secret_key="136MnvWAtoK0ixXa04sAnExcArNkSIcn",
#                         verify=True)

# keycloak_admin = KeycloakAdmin(connection=keycloak_connection)



# Configure client
keycloak_openid = KeycloakOpenID(server_url="http://0.0.0.0:8080/",
                                 client_id="myclient",
                                 realm_name="myrealm",
                                 client_secret_key="136MnvWAtoK0ixXa04sAnExcArNkSIcn")

# Get WellKnown
config_well_known = keycloak_openid.well_known()

#To get access token
access_token_url = "http://0.0.0.0:8080/realms/myrealm/protocol/openid-connect/token/"

client_id = 'myclient'
client_secret = '136MnvWAtoK0ixXa04sAnExcArNkSIcn'
payload = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

print("retriving token...")

response = requests.request("POST", access_token_url, headers=headers,data=payload)

access_token  =  json.loads(response.text).get('access_token')

# Post Api for creating user in keycloak

@app.post("/register/")
def register_user(username:str, firstName:str, lastName:str, email:str, password:str):
    add_user = "http://0.0.0.0:8080/admin/realms/myrealm/users/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    data = {
        "username": username,
        "firstName": firstName,
        "lastName": lastName,
        "email": email,
        "emailVerified": False,
        "enabled": True,
        "credentials": [
            {
                "temporary": False,
                "type": "password",
                "value": password
            }
        ]
    }

    data_json = json.dumps(data)
    response = requests.request("POST", add_user, headers=headers, data=data_json)
    print(response)
    if response.status_code == 201:
        return {"message": "User registered successfully"}
    else:
        return {"error": f"Failed to register user: {response.text}"}
    

# Login api for keycloak user with username and password
@app.post("/login")
def login(username: str, password: str):
    # Authenticate the user against Keycloak
    try:
        token = keycloak_openid.token(username, password)
        userinfo = keycloak_openid.userinfo(token['access_token'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Return the access token and user information
    return {"access_token": token['access_token'], "user_info": userinfo}