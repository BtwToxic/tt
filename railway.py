import requests, os

API = "https://backboard.railway.app/graphql"
KEY = os.getenv("API")

HEADERS = {
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

def gql(query, variables=None):
    r = requests.post(
        API,
        headers=HEADERS,
        json={"query": query, "variables": variables or {}}
    )
    return r.json()

# 🔹 LIST ALL SERVICES (already running ones)
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
                    id
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
    return gql(q, {"id": project_id})

# 🔴 STOP SERVICE
def stop_service(service_id):
    q = """
    mutation ($id: ID!) {
      serviceScale(serviceId: $id, replicas: 0) {
        id
      }
    }
    """
    return gql(q, {"id": service_id})

# 🟢 START SERVICE
def start_service(service_id):
    q = """
    mutation ($id: ID!) {
      serviceScale(serviceId: $id, replicas: 1) {
        id
      }
    }
    """
    return gql(q, {"id": service_id})

# 🔁 REDEPLOY
def redeploy(service_id):
    q = """
    mutation ($id: ID!) {
      serviceRedeploy(serviceId: $id) {
        id
      }
    }
    """
    return gql(q, {"id": service_id})
