import json
import importlib
from diagrams import Diagram, Cluster
from diagrams.azure.general import Managementgroups, Resourcegroups, Subscriptions
from diagrams.azure.identity import ActiveDirectory

# Load configuration data from config.json
with open('config.json') as config_file:
    data = json.load(config_file)

mg_labels = data["mg_labels"]
aad_label = data["aad_label"]
mg_subs_dict = data["mg_subs_dict"]
sub_labels = data["sub_labels"]
sub_rg_dict = data["sub_rg_dict"]
rg_resources_dict = data["rg_resources_dict"]
resource_mapping = data["resource_mapping"]

def create_management_groups(root_label, mg_subs_dict):
    with Cluster("Management Groups"):
        root = Managementgroups(root_label)
        mgs = {}
        for mg_label in mg_labels:
            mg = Managementgroups(mg_label)
            root - mg
            mgs[mg_label] = mg
        return root, mgs

def create_aad_cluster(aad_label):
    with Cluster("Azure Active Directory"):
        aad = ActiveDirectory(aad_label)
        return aad

def create_subscriptions(mg_subs_dict, mgs):
    with Cluster("Subscriptions"):
        subs = {}
        for mg_label, sub_labels in mg_subs_dict.items():
            for sub_label in sub_labels:
                sub = Subscriptions(sub_label)
                mgs[mg_label] - sub
                subs[sub_label] = sub
        return subs

def create_resource_groups(sub_rg_dict, subs):
    with Cluster("Resource Groups"):
        rgs = {}
        for sub_label, rg_labels in sub_rg_dict.items():
            for rg_label in rg_labels:
                rg = Resourcegroups(rg_label)
                subs[sub_label] - rg
                rgs[rg_label] = rg
        return rgs
    
def create_resources(rg_label, resources_list):
    resources = {}
    with Cluster(rg_label):
        for resource_dict in resources_list:
            resource_type = resource_dict["type"]
            resource_name = resource_dict["name"]
            
            module_name, class_name = resource_mapping[resource_type]
            module = importlib.import_module(f"diagrams.azure.{module_name}")
            resource_class = getattr(module, class_name)

            resource = resource_class(resource_name)
            resources[resource_name] = resource
    return resources

mg_subs = [sub for sublist in mg_subs_dict.values() for sub in sublist]
if not set(mg_subs) == set(sub_labels) == set(sub_rg_dict.keys()):
    print("Error: Subscription labels in mg_subs_dict, sub_rg_dict, and sub_labels do not match.")
    exit(1)

with Diagram("CAF Foundation Azure Landing Zone", show=False):
    root, mgs = create_management_groups("Root", mg_subs_dict)
    aad = create_aad_cluster(aad_label)
    root - aad

    subs = create_subscriptions(mg_subs_dict, mgs)

    rgs = create_resource_groups(sub_rg_dict, subs)

for rg_label in rg_resources_dict.keys():
    with Diagram(f"Resources in {rg_label}", show=False):
        rg = Resourcegroups(rg_label)
        resources_list = rg_resources_dict[rg_label]
        create_resources(rg_label, resources_list)
