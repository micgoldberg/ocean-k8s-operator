import os
from kubernetes import client, config, watch
from python_terraform import *
import base64

# Configure Kubernetes client
config.load_incluster_config()
v1 = client.CoreV1Api()
custom_api = client.CustomObjectsApi()

# Namespace and secret for Spot token/account
NAMESPACE = "spot-system"
SECRET_NAME = "ocean-controller-ocean-kubernetes-controller"

def get_operator_credentials():
    """Retrieve and decode Spot token and account from the Kubernetes secret."""
    print ('in get_operator_credentials')
    
    secret = v1.read_namespaced_secret('spotinst-secret', 'default')
    
    # Decode the base64-encoded secret values
    spot_token = base64.b64decode(secret.data['token']).decode('utf-8')
    spot_account = base64.b64decode(secret.data['account']).decode('utf-8')

    return spot_token, spot_account

# Initialize Terraform once
def init_terraform(terraform_dir):
    """Initialize Terraform and return the Terraform object."""
    tf = Terraform(working_dir=terraform_dir)
    print('Initializing Terraform...')
    
    # Initialize Terraform
    return_code, stdout, stderr = tf.init(capture_output=False, reconfigure=True)
    if return_code != 0:
        print(f"Error initializing Terraform: {stderr}")
        raise Exception("Failed to initialize Terraform")
    
    return tf

def apply_or_destroy_vng(tf, vng_spec):
    """Apply or destroy VNG based on the resource spec."""
    print ('in apply_or_destroy_vng')

    action = vng_spec['action']
    ocean_id = vng_spec['ocean_id']
    name = vng_spec['name']
    spot_percentage = vng_spec['spot_percentage']

    spot_token, spot_account = get_operator_credentials()

    tf_vars = {
        "spotinst_token": spot_token,
        "spotinst_account": spot_account,
        "name": name,
        "ocean_id": ocean_id,
        "spot_percentage": spot_percentage
    }

    print ('before if')
    
    if action == "apply":
        print ('in apply')
        print(f"Applying VNG: {name}")

        # Create or update the Terraform plan
        return_code, stdout, stderr = tf.plan_cmd(var=tf_vars, capture_output=False, out="init.tfplan")
        if return_code != 0:
            print(f"Error creating Terraform plan: {stderr}")
            raise Exception("Failed to create Terraform plan")
        
        return_code, stdout, stderr = tf.apply_cmd("init.tfplan", capture_output=False, parallelism=1)
        if return_code != 0:
            print(f"Error applying Terraform: {stderr}")
            raise Exception("Failed to apply Terraform")

    elif action == "destroy":
        print ('in destroy')
        print(f"Destroying VNG: {name}")

        return_code, stdout, stderr = tf.destroy_cmd(var=tf_vars, capture_output=False, auto_approve=True)
        if return_code != 0:
            print(f"Error destroying Terraform resources: {stderr}")
            raise Exception("Failed to destroy Terraform resources")

    else:
        print(f"Unknown action: {action}")

def watch_ocean_vng_events(tf):
    """Watch for OceanVNG resource events and process them."""
    print ('in watch_ocean_vng_events')
    w = watch.Watch()
    print ('after watch.Watch')

    for event in w.stream(custom_api.list_cluster_custom_object, group="spot.io", version="v1", plural="oceanvngs"):
        resource = event['object']
        event_type = event['type']
        vng_spec = resource['spec']
        print (vng_spec)

        if event_type in ["ADDED", "MODIFIED"]:
            apply_or_destroy_vng(tf, vng_spec)
        elif event_type == "DELETED":
            print(f"VNG resource deleted: {vng_spec['name']}")
            vng_spec['action'] = "destroy"
            apply_or_destroy_vng(tf, vng_spec)

if __name__ == "__main__":
    print ('in main')
    terraform_dir = '/usr/src/app/terraform'
    tf = init_terraform(terraform_dir)
    watch_ocean_vng_events(tf)