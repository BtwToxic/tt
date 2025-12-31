import requests
from config import RAILWAY_API_KEY

API = "https://backboard.railway.app/graphql"

HEADERS = {
    "Authorization": f"Bearer {RAILWAY_API_KEY}",
    "Content-Type": "application/json"
}

def gql(query, variables=None):
    if not RAILWAY_API_KEY:
        return {}

    try:
        r = requests.post(
            API,
            headers=HEADERS,
            json={"query": query, "variables": variables or {}},
            timeout=8
        )
        return r.json()
    except Exception as e:
        print("Railway API error:", e)
        return {}

# 🔹 ALL PROJECTS
def list_projects():
    q = """
    {
      projects {
        edges {
          node {
            id
            name
          }
        }
      }
    }
    """
    data = gql(q)
    return data.get("data", {}).get("projects", {}).get("edges", [])

# 🔹 SERVICES OF A PROJECT
def list_services(project_id):
    q = """
    query ($id: ID!) {
      project(id: $id) {
        services {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
    """
    data = gql(q, {"id": project_id})
    return (
        data.get("data", {})
        .get("project", {})
        .get("services", {})
        .get("edges", [])
    )

# 🔹 ACTIONS
def scale(service_id, replicas):
    q = """
    mutation ($id: ID!, $r: Int!) {
      serviceScale(serviceId: $id, replicas: $r) {
        id
      }
    }
    """
    gql(q, {"id": service_id, "r": replicas})

def redeploy(service_id):
    q = """
    mutation ($id: ID!) {
      serviceRedeploy(serviceId: $id) {
        id
      }
    }
    """
    gql(q, {"id": service_id})
