#!/usr/bin/python3
"""
This example covers the following:
    - Create deployment
    - Annotate deployment
"""
AUTH_PORT = 3001
DIRS_PORT = 3002
BLOB_PORT = 3003

from kubernetes import client, config
import argparse
import uuid
import os,sys


# URI_AUTH=$1
# ADMIN=$2
# ADDRESS=$3
# PORT_AUTH=$4
# PORT_DIR=$5
# PORT_BLOB=$6
# DB_AUTH=$7
# DB_DIR=$8
# DB_BLOB=$9
def create_deployment_object(args):
    
    container = client.V1Container(
        name="restfs-container",
        image="josemimo2/restfs_full:latest",
        image_pull_policy="Always",
        ports=[client.V1ContainerPort(container_port=args.aport),client.V1ContainerPort(container_port=args.dport),client.V1ContainerPort(container_port=args.bport)],
        args=[str(args.pos_arg),str(args.admin),str(args.listening),str(args.aport),str(args.dport),str(args.bport),str(args.authdb),str(args.dirsdb),str(args.blobdb)]
    )
    # Template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "restfs"}),
        spec=client.V1PodSpec(containers=[container]))
    # Spec
    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={"app": "restfs"}
        ),
        template=template)
    # Deployment
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="deploy-restfs"),
        spec=spec)

    return deployment


def create_deployment(apps_v1_api, deployment_object):
    # Create the Deployment in default namespace
    # You can replace the namespace with you have created
    apps_v1_api.create_namespaced_deployment(
        namespace="default", body=deployment_object
    )


def main():

    if len(sys.argv) < 1:
        print("Introducir por lo menos 1 argumento: URL de Auth API")
        sys.exit()
        
    # Loading the local kubeconfig
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()

    token = str(uuid.uuid4())
    direccion = "0.0.0.0"
    auth_path = "/db_auth"
    dirs_path = "/db_dirs"
    blob_path = "/db_files"
    
    parser = argparse.ArgumentParser(description="Restdir arguments")
    parser.add_argument('pos_arg', type=str, help='URL de la API de autenticación') #<- URl api auth
    parser.add_argument("-a", "--admin", help='Token de admin', action='store', default=token, type=str)
    parser.add_argument("-ap", "--aport", help='Puerto de escucha API auth', action='store', default=AUTH_PORT, type=int)
    parser.add_argument("-dp", "--dport", help='Puerto de escucha API dirs', action='store', default=DIRS_PORT, type=int)
    parser.add_argument("-bp", "--bport", help='Puerto de escucha API blob', action='store', default=BLOB_PORT, type=int)
    parser.add_argument("-l", "--listening", help='Dirección IP API', action='store', default=direccion, type=str)
    parser.add_argument("-ad", "--authdb", help='Ruta de la db de auth', action='store', default=auth_path, type=str)
    parser.add_argument("-bd", "--blobdb", help='Ruta del storage de blob', action='store', default=blob_path, type=str)
    parser.add_argument("-dd", "--dirsdb", help='Ruta de la db de dirs', action='store', default=dirs_path, type=str)

    args = parser.parse_args()

    deployment_obj = create_deployment_object(args)

    create_deployment(apps_v1_api, deployment_obj)

    os.system("kubectl expose deployment deploy-restfs --type=NodePort --name=auth-service --external-ip=192.168.1.100 --port="+str(args.aport)+" --target-port="+str(args.aport)+"")
    os.system("kubectl expose deployment deploy-restfs --type=NodePort --name=dirs-service --external-ip=192.168.1.100 --port="+str(args.dport)+" --target-port="+str(args.dport)+"")
    os.system("kubectl expose deployment deploy-restfs --type=NodePort --name=blob-service --external-ip=192.168.1.100 --port="+str(args.bport)+" --target-port="+str(args.bport)+"")

if __name__ == "__main__":
    main()






