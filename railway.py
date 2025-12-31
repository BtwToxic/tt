import requests, json

cfg = json.load(open("config.json"))

API = "https://backboard.railway.app/graphql"
HEADERS = {
    "Authorization": f"Bearer {cfg['railway_api_key']}",
    "Content-Type": "application/json"
}

def list_services():
    q = """
    query($id:ID!){
      project(id:$id){
        services{edges{node{id name}}}
      }
    }"""
    r = requests.post(API, json={
        "query": q,
        "variables": {"id": cfg["railway_project_id"]}
    }, headers=HEADERS)
    return r.json()["data"]["project"]["services"]["edges"]
