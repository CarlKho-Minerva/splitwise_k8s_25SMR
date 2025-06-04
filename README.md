# My Kubernetes (with Minikube) & Docker Cheatsheet for Splitwise Project

This guide summarizes the essential commands and concepts used to develop, containerize, and deploy the Simple Splitwise application on a local Minikube Kubernetes cluster.

## 1. FastAPI Application (Local Development)

* **Run the FastAPI app locally (before Docker/Kubernetes):**

    ```bash
    # Make sure you are in the directory with main.py and requirements.txt
    # Install dependencies if you haven't: pip install -r requirements.txt
    uvicorn main:app --reload
    ```

  * Access API docs: `http://127.0.0.1:8000/docs`
  * Access greeting: `http://127.0.0.1:8000/greeting`

## 2. Docker Commands

* **Build a Docker Image:**
    From the directory containing your `Dockerfile`, `main.py`, `requirements.txt`:

    ```bash
    docker build -t <image_name>:<tag> .
    # Example:
    docker build -t simple-splitwise:v1 .
    ```

* **List Docker Images:**

    ```bash
    docker images
    ```

* **Run a Docker Container:**

    ```bash
    docker run -d -p <host_port>:<container_port> --name <container_name> <image_name>:<tag>
    # Example:
    docker run -d -p 8080:80 --name splitwise-app simple-splitwise:v1
    ```

  * `-d`: Detached mode (run in background)
  * `-p`: Port mapping (host:container)
  * `--name`: Assign a name to the container

* **List Running Containers:**

    ```bash
    docker ps
    ```

* **List All Containers (running and stopped):**

    ```bash
    docker ps -a
    ```

* **View Container Logs:**

    ```bash
    docker logs <container_name_or_id>
    # Example:
    docker logs splitwise-app
    ```

* **Stop a Container:**

    ```bash
    docker stop <container_name_or_id>
    # Example:
    docker stop splitwise-app
    ```

* **Remove a Stopped Container:**

    ```bash
    docker rm <container_name_or_id>
    # Example:
    docker rm splitwise-app
    ```

* **Remove a Docker Image:**
    (Ensure no containers are using it)

    ```bash
    docker rmi <image_name>:<tag>
    # Example:
    docker rmi simple-splitwise:v1
    ```

## 3. Minikube Commands (Local Kubernetes Cluster)

* **Start Minikube Cluster:**
    (Specify driver if needed, e.g., `--driver=docker`)

    ```bash
    minikube start
    ```

* **Stop Minikube Cluster:**

    ```bash
    minikube stop
    ```

* **Check Minikube Status:**

    ```bash
    minikube status
    ```

* **Get Minikube IP Address:**
    (Useful for accessing NodePort services)

    ```bash
    minikube ip
    ```

* **Load Local Docker Image into Minikube's Docker Daemon:**
    (Crucial for Minikube to find locally built images without a remote registry)

    ```bash
    minikube image load <image_name>:<tag>
    # Example:
    minikube image load simple-splitwise:v1
    ```

* **Access a Service Running in Minikube:**
    (Opens the service in your browser, often handles port-forwarding/tunneling)

    ```bash
    minikube service <service_name>
    # Example:
    minikube service simple-splitwise-service
    ```

* **Run Minikube Tunnel (for LoadBalancer services):**
    (Run in a separate terminal; provides an external IP for LoadBalancer services)

    ```bash
    minikube tunnel
    ```

## 4. `kubectl` Commands (Interacting with Kubernetes)

**General Tip:** Consider aliasing `kubectl` to `k` in your shell (`alias k='kubectl'`).

* **Apply Configuration from a YAML File:**
    (Creates or updates resources)

    ```bash
    kubectl apply -f <filename.yaml_or_directory>
    # Example:
    kubectl apply -f splitwise-deployment.yaml
    kubectl apply -f . # Apply all YAML files in current directory
    ```

* **Get Information About Resources:**

    ```bash
    kubectl get <resource_type>
    kubectl get <resource_type> <resource_name>
    kubectl get <resource_type> -n <namespace> # For a specific namespace
    kubectl get <resource_type> -o wide        # More details
    kubectl get <resource_type> -o yaml        # Get resource definition as YAML
    kubectl get <resource_type> -w             # Watch for changes
    ```

  * **Common Resource Types & Shorthands:**
    * `pods` (`po`)
    * `deployments` (`deploy`)
    * `services` (`svc`)
    * `persistentvolumeclaims` (`pvc`)
    * `persistentvolumes` (`pv`)
    * `configmaps` (`cm`)
    * `namespaces` (`ns`)
    * `nodes` (`no`)
  * **Examples:**

        ```bash
        kubectl get pods
        kubectl get pods -w
        kubectl get deployment simple-splitwise-deployment
        kubectl get svc
        kubectl get pvc simple-splitwise-pvc -o wide
        ```

* **Describe a Resource (Detailed Information & Events):**

    ```bash
    kubectl describe <resource_type> <resource_name>
    # Example:
    kubectl describe deployment simple-splitwise-deployment
    kubectl describe pod <pod_name_from_get_pods>
    kubectl describe service simple-splitwise-service
    ```

* **View Logs from a Pod's Container:**

    ```bash
    kubectl logs <pod_name>
    kubectl logs <pod_name> -c <container_name> # If multiple containers in pod
    kubectl logs -f <pod_name>                  # Follow logs (stream)
    # Example:
    kubectl logs simple-splitwise-deployment-xxxx-yyyy
    ```

* **Execute a Command Inside a Pod's Container:**

    ```bash
    kubectl exec <pod_name> -- <command> <args...>
    kubectl exec -it <pod_name> -- /bin/bash   # Interactive shell (if bash exists)
    # Example:
    kubectl exec <pod_name> -- printenv | grep APP_GREETING
    kubectl exec <pod_name> -- ls -l /data
    kubectl exec <pod_name> -- cat /data/splitwise_data.json
    ```

* **Scale a Deployment:**

    ```bash
    kubectl scale deployment <deployment_name> --replicas=<count>
    # Example:
    kubectl scale deployment simple-splitwise-deployment --replicas=3
    ```

* **Manage Deployments Rollouts:**
  * **Check rollout status:**

        ```bash
        kubectl rollout status deployment/<deployment_name>
        # Example:
        kubectl rollout status deployment/simple-splitwise-deployment
        ```

  * **View rollout history:**

        ```bash
        kubectl rollout history deployment/<deployment_name>
        ```

  * **Rollback to a previous revision:**

        ```bash
        kubectl rollout undo deployment/<deployment_name>
        kubectl rollout undo deployment/<deployment_name> --to-revision=<revision_number>
        ```

  * **Trigger a new rollout (e.g., to pick up ConfigMap changes consumed as env vars):**

        ```bash
        kubectl rollout restart deployment/<deployment_name>
        ```

* **Delete Resources:**
  * **By name:**

        ```bash
        kubectl delete <resource_type> <resource_name>
        # Example:
        kubectl delete pod <pod_name>
        ```

  * **From a YAML file (deletes resources defined in the file):**

        ```bash
        kubectl delete -f <filename.yaml>
        # Example:
        kubectl delete -f splitwise-deployment.yaml
        ```

  * **Delete all resources with a specific label:**

        ```bash
        kubectl delete <resource_type> -l <label_key>=<label_value>
        # Example: kubectl delete pods -l app=simple-splitwise
        ```

* **Get Help/Explain Kubernetes API Objects:**
    (Very useful for understanding fields in YAML)

    ```bash
    kubectl explain <resource_type>
    kubectl explain <resource_type>.<field_name>
    # Example:
    kubectl explain deployment
    kubectl explain deployment.spec
    kubectl explain deployment.spec.template.spec.containers
    ```

## 5. Kubernetes YAML Manifest Files - Key Structure

All Kubernetes object definitions in YAML typically have these top-level fields:

* **`apiVersion`**: (e.g., `v1`, `apps/v1`) The API version for this object type.
* **`kind`**: (e.g., `Pod`, `Deployment`, `Service`, `ConfigMap`, `PersistentVolumeClaim`) The type of Kubernetes object.
* **`metadata`**: Information about the object instance.
  * `name`: Unique name for the object (within its namespace).
  * `labels`: Key-value pairs for organizing and selecting objects.
  * `namespace`: (Optional) The namespace for this object.
* **`spec`**: The **desired state** of the object. The content of `spec` varies greatly depending on the `kind`.

**Example `Deployment` Key `spec` Fields:**

```yaml
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app # Must match labels in template.metadata.labels
  template: # Pod template
    metadata:
      labels:
        app: my-app
    spec: # Pod specification
      containers:
      - name: my-container
        image: my-image:tag
        ports:
        - containerPort: 80
        env: # Environment variables
          - name: MY_ENV_VAR
            value: "some_value"
          - name: VAR_FROM_CONFIGMAP
            valueFrom:
              configMapKeyRef:
                name: my-configmap
                key: my-key
        volumeMounts: # Mount volumes into container
          - name: my-volume-storage
            mountPath: /data
      volumes: # Define volumes for the Pod
        - name: my-volume-storage
          persistentVolumeClaim:
            claimName: my-pvc-name


Example Service Key spec Fields:

spec:
  type: NodePort # or ClusterIP, LoadBalancer
  selector:
    app: my-app # Selects Pods with this label
  ports:
    - protocol: TCP
      port: 80       # Port on the Service's ClusterIP
      targetPort: 8080 # Port on the Pods/containers
      # nodePort: 30080 # Optional for NodePort type
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Yaml
IGNORE_WHEN_COPYING_END

This should serve as a solid starting point for your notes! As you continue your Kubernetes journey, you'll add more to it.

This Markdown file should be a great help if you decide to tackle this project again or work on similar ones. You can keep adding to it as you learn more commands or tricks!
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END
