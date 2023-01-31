# Creación de la plataforma - K8S cluster

## Archivos

- /deployment/deploy.py: script de lanzamiento del despliegue utilizando Python+K8S.
- /docker: carpeta con los paquetes (src) de cada servicio y los archivos para la contruccion de la imagen docker.
- /config: carpeta donde encontramos archivos necesarios para la creación de la plataforma
- build.sh: script para la creación de la imagen. En nuestro caso al estar la imagen actualizada en Docker Hub no es necesario ejecutarlo.

## Guia paso a paso

1. **Creamos las 2 maquinas virtuales con VirtualBox**

> Nota: antes de nada debemos establecer la asignación de dirección IP de forma estática en ambas máquinas. Por dos razones:
- Para acceder a las máquinas mediante ssh de una forma más sencilla.
- Para que la dirección del nodo master (Director) sea siempre la misma

```
cambiamos en /etc/network/interfaces
inet dhcp -> inet static
address 192.168.1.147 (worker)

address 192.168.1.148 (director)
```

2. **Instalamos en ambas docker.**

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

3. **Instalamos las herramientas necesarias para hacer una plataforma K8S vanilla: kubeadm, kubectl, kubelet:**

Para instalar kubeadm, kubectl, kubelet:

```
$ sudo apt-get update
$ sudo apt-get install -y apt-transport-https ca-certificates curl

$ sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg

$ echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

$ sudo apt-get update
$ sudo apt-get install -y kubelet kubeadm kubectl
$ sudo apt-mark hold kubelet kubeadm kubectl
```

> Nota: para poder iniciar un cluster, primero debemos deshabilitar el swap space y habilitar el ip forwarding:

```
$ nano /etc/fstab

comentar la linea de swap

$ sudo swapoff -a
```

```
$ sudo nano /etc/sysctl.conf

descomentamos la linea: net.ipv4.ip_forward=1
```

4. **Iniciamos el cluster en la maquina _director_ (la que actua de nodo master):**

```
#para arreglar el error de CRI
$ sudo apt remove containerd
$ sudo apt install containerd.io
$ rm /etc/containerd/config.toml
$ systemctl restart containerd

$ sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```

Después el comando nos indicará unos pasos para poder iniciar el cluster

```
$ mkdir -p $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config 
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

> Nota: para evitar que el kubelet produzca crash debido a la configuración de los cgroup, añadimos el contenido del archivo **config.toml** de la carpeta **config** en la siguiente ruta

```
$  touch /etc/containerd/config.toml
```

5. **Para que los contenedores puedan comunicarse dentro del cluster necesitamos un add-on para la política de red (usamos _Calico_ y el contenido del archivo de configuración _custom-resources.yaml_)**

```
$ kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.25.0/manifests/tigera-operator.yaml

$ kubectl create -f ./custom-resources.yaml

$ kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

6. **Añadimos el nodo worker al cluster**

```
$ sudo kubeadm join 192.168.148:6443 <informacion_obtenida_init>
```

> En caso de que hayamos perdido el comando de join, introducimos:

```
$ kubeadm token create --print-join-command
```

# Despliegue de la aplicación en el Cluster

1. **(PASO OPCIONAL)**

Una vez tenemos el Dockerfile y los archivos source (en la carpeta /docker), utilizaremos el shell script de la anterior entrega para buildear la imagen del docker:**

```
$ ./build.sh
```

> Nota: para poder desplegar la aplicacion en el cluster debemos tener en cuenta que la imagen generada del docker debe ser subida a Docker Hub, para poder automatizar el pull de la misma al hacer el contenedor.

Ahora, una vez tenemos la imagen actualizada en Docker Hub debemos preparar su deployment en el cluster:

2. **Para hacer el deployment debemos ejecutar el script _deploy.py_, donde se establece la configuración del contenedor o pod que aloja los servicios de directorios, blob y autenticación.**


> Nota: para automatizar el despliegue de la aplicación hemos utilizado el cliente de Python para K8s (Kubernetes), cuya instalación debemos hacer localmente al director:

```
$ pip install kubernetes
```

Para realizar el despliegue introducimos:

```
$ python3 ./deployment/deploy.py <url de autenticación> 
```

Donde los argumentos opcionales son:

- -a, --admin: token de administrador. Por defecto: valor random generado 
- -ap, --aport: puerto de escucha API auth. Por defecto: 3001
- -dp, --dport: puerto de escucha API dirs. Por defecto: 3002
- -bp, --bport: puerto de escucha API blob. Por defecto: 3003
- -l, --listening: dirección IP API. Por defecto: 0.0.0.0
- -ad, --authdb: ruta de la db de auth. Por defecto: /db_auth
- -bd, --blobdb: ruta del storage de blob. Por defecto: /db_files
- -dd, --dirsdb: ruta de la db de dirs. Por defecto: /db_dirs
- -h, --help: opción indica todos los argumentos y sus valores.


> Nota: tener en cuenta que aunque el argumento --aport (puerto de auth) es opcional, el puerto que se indique en la URL de autenticación debe ser el mismo a este.

En el propio archivo de deploy hacemos la exposición de los tres servicios, así podrán ser accedidos desde fuera del cluster (usando la dirección IP del control-plane (director)).

# Pruebas de cliente

La API puede ser probada con el archivo **main.py** del paquete restfs_client. Tener en cuenta que este paquete debe estar instalado en el host fuera o dentro del cluster.



