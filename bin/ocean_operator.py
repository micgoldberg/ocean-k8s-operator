import os
from kubernetes import client, config, watch
from python_terraform import Terraform

# Configure Kubernetes client
config.load_incluster_config()
v1 = client.CoreV1Api()
custom_api = client.CustomObjectsApi()

# Namespace and secret for Spot token/account
NAMESPACE = "spot-system"
SECRET_NAME = "ocean-controller-ocean-kubernetes-controller"

def get_spot_credentials():
    """Retrieve Spot token and account from the Kubernetes secret."""
    secret = v1.read_namespaced_secret(SECRET_NAME, NAMESPACE)
    spot_token = secret.data['spot_token']  # Assumes base64 encoded in secret
    spot_account = secret.data['spot_account']
    return spot_token, spot_account

def apply_or_destroy_vng(vng_spec):
    """Apply or destroy VNG based on the resource spec."""
    action = vng_spec['action']
    ocean_id = vng_spec['ocean_id']
    name = vng_spec['name']
    spot_percentage = vng_spec['spot_percentage']

    spot_token, spot_account = get_spot_credentials()

    # Initialize Terraform
    tf = Terraform()
    tf_vars = {
        "spotinst_token": spot_token,
        "spotinst_account": spot_account,
        "name": name,
        "ocean_id": ocean_id,
        "spot_percentage": spot_percentage
    }

    if action == "apply":
        print(f"Applying VNG: {name}")
        tf.apply(var=tf_vars, capture_output=False)
    elif action == "destroy":
        print(f"Destroying VNG: {name}")
        tf.destroy(var=tf_vars, capture_output=False)
    else:
        print(f"Unknown action: {action}")

def watch_ocean_vng_events():
    """Watch for OceanVNG resource events and process them."""
    w = watch.Watch()
    for event in w.stream(custom_api.list_cluster_custom_object, group="spot.io", version="v1", plural="oceanvngs"):
        resource = event['object']
        event_type = event['type']
        vng_spec = resource['spec']
        print (vng_spec)

        if event_type in ["ADDED", "MODIFIED"]:
            apply_or_destroy_vng(vng_spec)
        elif event_type == "DELETED":
            print(f"VNG resource deleted: {vng_spec['name']}")
            vng_spec['action'] = "destroy"
            apply_or_destroy_vng(vng_spec)

if __name__ == "__main__":
    watch_ocean_vng_events()
