# Deploy de la plataforma + K8S cluster

1. Creamos las 2 maquinas virtuales con VirtualBox

>Nota: antes de nada debemos establecer la asignación de dirección IP de forma estática en ambas máquinas. Por dos razones:
    - Para acceder a las máquinas mediante ssh de una forma más sencilla.
    - Para que la dirección del nodo master (Director) sea siempre la misma

```
cambiamos en /etc/network/interfaces
inet dhcp -> inet static
address 192.168.1.147 (worker)

address 192.168.1.148 (director)
```

2. Instalamos en ambas docker.

```
$ sudo apt-get update
$ sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

$ sudo mkdir -p /etc/apt/keyrings
$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

$ echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

3. Kubernetes vanilla -> insalar con kubeadm

> Para instalar kubeadm, kubectl, kubelet:

```
https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/

$ sudo apt-get update
$ sudo apt-get install -y apt-transport-https ca-certificates curl

$ sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

$ echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

$ sudo apt-get update
$ sudo apt-get install -y kubelet kubeadm kubectl
$ sudo apt-mark hold kubelet kubeadm kubectl
```
> Para poder iniciar un cluster, primero debemos deshabilitar el swap space:

```
$ nano /etc/fstab

comentar la linea de swap

$ sudo swapoff -a
```

> Habilitar IP forwarding para la comunicación con los nodos worker?

```
$ sudo nano /etc/sysctl.conf

descomentamos la linea: net.ipv4.ip_forward=1
```

### IPs --> worker 192.168.1.147, director 192.168.1.148



4. Iniciamos el cluster en la maquina **director** :

```
#para arreglar el error de CRI
$ sudo apt remove containerd
$ sudo apt install containerd.io
$ rm /etc/containerd/config.toml
$ systemctl restart containerd

$ sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```

> Después el comando nos indicará unos pasos para poder iniciar el cluster

```
$ mkdir -p $HOME/.kube 
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config 
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

> Para que el kubelet no produzca crasheo y poder configurar los cgroup:

```
 Añadimos el siguiente contenido al archivo /etc/containerd/config.toml

$ touch /etc/containerd/config.toml

# Content of file /etc/containerd/config.toml
version = 2
[plugins]
  [plugins."io.containerd.grpc.v1.cri"]
   [plugins."io.containerd.grpc.v1.cri".containerd]
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          runtime_type = "io.containerd.runc.v2"
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            SystemdCgroup = true
```

5. Para que los contenedores puedan comunicarse dentro del cluster necesitamos un add-on para la política de red (usamos Calico)

```
$ kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.0/manifests/tigera-operator.yaml

#(archivo local con cidr cambiado por 10.0.0.0/16)
$ kubectl create -f ./custom-resources.yaml 

$ kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

6. Añadimos el nodo worker al cluster

```
$ sudo kubeadm join 192.168.148:6443 <informacion_obtenida_init>
```

# Deployment de la aplicación en el Cluster

Para poder desplegar la aplicacion en el cluster debemos almacenar localmente en nodo maestro la aplicación virtualizada en Docker.
Utilizaremos el siguiente para ello:

``` 
$ scp <directorio_docker> <usuario>@director: .
```

Una vez tenemos el Dockerfile y los archivos source, utilizaremos el shell script de la anterior entrega para buildear la imagen del docker:

```
$ ./build.sh
```

Ahora, una vez tenemos la imagen del Docker debemos preparar su deployment en el cluster:

> Nota: para automatizar el despliegue de la aplicación hemos utilizado el cliente de Python para K8s (Kubernetes), cuya instalación debemos hacer localmente al director:

```
$ pip install kubernetes
```

1. Para realizar el deployment debemos indicar la configuración del contenedor o pod que aloja la aplicación. Seguimos la siguiente configuración:

> En su versión .yaml:

```
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: deploy-dirapi
    namespace: default
    spec:
        replicas: 1
    template:
        metadata:
            labels:
                app: dirapi
        spec:
            containers:
            - name: dirapi-container
              image: debian-dirapi
              imagePullPolicy: Always
              volumeMount:
                -mountPath: ${args.db}
                 name: dirdb
              ports:
                -containerPort: ${args.port}
              args: [${args.pos_arg}, ${args.db}, ${args.admin}, ${args.listening}, ${args.port}]
            volumes:
                name: dirdb
```

> En la implementación .py:

```
    volume = client.V1Volume(
        name="dirdb"
    ) 
    container = client.V1Container(
        name="dirapi-container",
        image="josemimo2/debian-dirapi:latest",
        image_pull_policy="Always",
        volume_mounts=[client.V1VolumeMount(name="dirdb", mount_path=args.db)],
        ports=[client.V1ContainerPort(container_port=args.port)],
        args=[str(args.pos_arg), str(args.db), str(args.admin), str(args.listening), str(args.port)]
    )
    # Template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "dirapi"}),
        spec=client.V1PodSpec(containers=[container], volumes=[volume],restart_policy="Always"))
    # Spec
    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(
            match_labels={"app": "dirapi"}
        ),
        template=template)
    # Deployment
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="deploy-dirapi"),
        spec=spec)
```

2. Simplemente nos reducimos a ejecutar el script **deploy.py** 

```
$ python3 deploy.py <arg1> -a <arg2> -d <arg3> -l <arg4> -p <arg5>
```

3. Exponemos la aplicación mediante un servicio del tipo NodePort, así podrá ser accedido desde fuera del cluster:

```
# En el propio archivo deploy.py
$ os.system(kubectl expose deployment deploy-dirapi --type=NodePort --name=flask-service --port=80 --target-port=3002)
```

