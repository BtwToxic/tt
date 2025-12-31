import requests
from config import RAILWAY_API_KEY

API = "https://backboard.railway.app/graphql/v2"

HEADERS = {
    "Authorization": f"Bearer {RAILWAY_API_KEY}",
    "Content-Type": "application/json"
}

def gql(query, variables=None):
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

# 🔹 PROJECTS
def list_projects():
    q = """{ projects { edges { node { id name }}}}"""
    data = gql(q)
    return data.get("data", {}).get("projects", {}).get("edges", [])

# 🔹 SERVICES (FILTER DELETED)
def list_services(project_id):
    q = """
    query ($id: ID!) {
      project(id: $id) {
        services {
          edges {
            node {
              id
              name
              deployments(last:1) {
                edges {
                  node {
                    status
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = gql(q, {"id": project_id})
    services = (
        data.get("data", {})
        .get("project", {})
        .get("services", {})
        .get("edges", [])
    )

    # filter deleted / broken
    clean = []
    for s in services:
        if s.get("node") and s["node"].get("name"):
            clean.append(s)
    return clean

# 🔹 LOGS
def service_logs(service_id):
    q = """
    query ($id: ID!) {
      service(id: $id) {
        logs(limit: 100)
      }
    }
    """
    data = gql(q, {"id": service_id})
    return data.get("data", {}).get("service", {}).get("logs", [])

# 🔹 METRICS
def service_metrics(service_id):
    q = """
    query ($id: ID!) {
      service(id: $id) {
        metrics {
          cpu
          memory
        }
      }
    }
    """
    data = gql(q, {"id": service_id})
    return data.get("data", {}).get("service", {}).get("metrics", {})

# 🔹 CONTROLS
def start_service(service_id):
    gql("""mutation($id:ID!){serviceScale(serviceId:$id,replicas:1){id}}""", {"id": service_id})

def stop_service(service_id):
    gql("""mutation($id:ID!){serviceScale(serviceId:$id,replicas:0){id}}""", {"id": service_id})

def restart_service(service_id):
    gql("""mutation($id:ID!){serviceRedeploy(serviceId:$id){id}}""", {"id": service_id})
