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
```

Example Service Key spec Fields:
```yaml
spec:
  type: NodePort # or ClusterIP, LoadBalancer
  selector:
    app: my-app # Selects Pods with this label
  ports:
    - protocol: TCP
      port: 80       # Port on the Service's ClusterIP
      targetPort: 8080 # Port on the Pods/containers
      # nodePort: 30080 # Optional for NodePort type
```

## 6. Common Sequences of Operations

This section outlines common sequences of operations I have performed.

### A. Updating Application Code (e.g., changes in `main.py`)

1.  **Modify Application Code:** Make your changes in `main.py` or other application files.
2.  **Increment Image Version:** Decide on a new image tag (e.g., if current is `:v3`, new one is `:v4`).
3.  **Build New Docker Image:**
    ```bash
    docker build -t simple-splitwise:v<new_version> .
    # Example: docker build -t simple-splitwise:v4 .
    ```
4.  **Load Image into Minikube:**
    ```bash
    minikube image load simple-splitwise:v<new_version>
    # Example: minikube image load simple-splitwise:v4
    ```
5.  **Update Deployment YAML:**
    Edit your `splitwise-deployment.yaml` (or relevant deployment file):
    *   Change the `spec.template.spec.containers[0].image` field to the new image tag.
      ```yaml
      # ...
      spec:
        template:
          spec:
            containers:
            - name: splitwise-app-container
              image: simple-splitwise:v<new_version> # <-- UPDATE HERE
      # ...
      ```
6.  **Apply Updated Deployment:**
    This will trigger a rolling update.
    ```bash
    kubectl apply -f splitwise-deployment.yaml
    ```
7.  **Monitor Rollout:**
    ```bash
    kubectl rollout status deployment/simple-splitwise-deployment
    kubectl get pods -w # To see Pods being replaced
    ```
8.  **Test:** Access your application via its Service to verify changes.

### B. Changing Application Configuration (via ConfigMap - Environment Variables)

1.  **Modify ConfigMap YAML:**
    Edit your `splitwise-configmap.yaml` (or relevant ConfigMap file) with the new configuration values.
    ```yaml
    # ... in splitwise-configmap.yaml
    data:
      APP_GREETING: "New greeting from updated ConfigMap!" # <-- UPDATE HERE
    # ...
    ```
2.  **Apply Updated ConfigMap:**
    ```bash
    kubectl apply -f splitwise-configmap.yaml
    ```
3.  **Trigger Deployment Rollout:**
    For environment variables sourced from ConfigMaps to be picked up by existing Pods, the Pods generally need to be restarted. The easiest way is to trigger a rollout of the Deployment that consumes the ConfigMap:
    ```bash
    kubectl rollout restart deployment/simple-splitwise-deployment
    ```
4.  **Monitor Rollout:**
    ```bash
    kubectl rollout status deployment/simple-splitwise-deployment
    kubectl get pods -w
    ```
5.  **Test:** Access your application and verify the new configuration is active (e.g., check the `/greeting` endpoint).

### C. Starting Fresh / Full Redeploy (from scratch after stopping Minikube)

1.  **Start Docker Desktop** (if not already running).
2.  **Start Minikube:**
    ```bash
    minikube start
    ```
3.  **Load Latest Docker Image into Minikube (if not already there or if you cleared Minikube):**
    ```bash
    minikube image load simple-splitwise:v<latest_version>
    ```
4.  **Apply All Kubernetes Manifests:**
    It's often easiest to apply them in order of dependency, but `kubectl apply -f .` in a directory with all your YAMLs can work if dependencies are well-managed (or apply individually):
    *   ConfigMap (if any): `kubectl apply -f splitwise-configmap.yaml`
    *   PersistentVolumeClaim (PVC): `kubectl apply -f splitwise-pvc.yaml`
    *   Deployment: `kubectl apply -f splitwise-deployment.yaml`
    *   Service: `kubectl apply -f splitwise-service.yaml`
5.  **Check Status of All Components:**
    ```bash
    kubectl get all # Shows common resources
    kubectl get pvc
    kubectl get deployment
    kubectl get pods -w
    kubectl get service
    ```
6.  **Access Service:**
    ```bash
    minikube service simple-splitwise-service
    ```

### D. Debugging a Failing Pod

1.  **Get Pod Name & Status:**
    ```bash
    kubectl get pods
    # Look for Pods with status like CrashLoopBackOff, Error, ImagePullBackOff
    ```
2.  **Describe the Pod:**
    This often gives clues in the `Events` section at the bottom.
    ```bash
    kubectl describe pod <failing_pod_name>
    ```
    *   Look for events like "Failed to pull image," "Back-off restarting failed container," readiness/liveness probe failures.
3.  **Check Logs:**
    *   For current run: `kubectl logs <failing_pod_name>`
    *   For previous run (if it crashed and restarted): `kubectl logs --previous <failing_pod_name>`
4.  **If `ImagePullBackOff`:**
    *   Ensure image name and tag are correct in `Deployment` YAML.
    *   Ensure image is loaded into Minikube: `minikube image load <image>:<tag>`
    *   Check `imagePullPolicy` in Deployment YAML.
5.  **If `CrashLoopBackOff`:** The application inside the container is crashing repeatedly.
    *   Check `kubectl logs` for application errors.
    *   If logs are too brief, try `kubectl logs --previous`.
    *   Consider if it's a configuration issue (ConfigMap values, missing Secrets), file permission issue on mounted volumes, or a bug in the application code.
    *   You can try `kubectl exec -it <pod_name> -- /bin/sh` (if the image has a shell) to poke around, but if it's crashing quickly, this might be hard.

### E. Stopping Work and Reclaiming Resources

1.  **Stop Minikube:**
    ```bash
    minikube stop
    ```
2.  **Quit Docker Desktop.**

## 7. Insights & Tips for Carl

*   **Embrace Aliases & Autocompletion Early:** You mentioned the amount of typing.
    *   `alias k='kubectl'` is your best friend.
    *   Set up `kubectl completion` for your shell (Bash/Zsh). It will dramatically speed things up and reduce typos for resource names and commands.
*   **The "Why" Behind Nested `spec`s:** You quickly picked up on the compositional nature of Kubernetes YAMLs (e.g., a Deployment's `spec` contains a Pod `template` which has its own `spec`). Understanding this hierarchy is key to writing correct manifests. The visual diagram we discussed helped here. Remember, higher-level objects define *how to create and manage* lower-level ones.
*   **`minikube service` vs. `NodePort` IP:** Your experience with the Docker driver on macOS and the `minikube service` command creating a tunnel (`127.0.0.1:<port>`) is a common point of confusion. For local development with this setup, rely on the URL provided by `minikube service` after the tunnel starts. This doesn't mean `NodePort` is broken; it's just how Minikube makes it accessible on your specific OS/driver combo.
*   **Persistence is Key for "Real" Apps:** You saw the impact of adding the PVC. For almost any app you want to use beyond a quick demo, persistent storage (or a proper external database that uses it) is crucial. The PV/PVC/StorageClass dance is fundamental.
*   **Iterative Development Cycle:** The workflow of:
    1.  Code change (`main.py`)
    2.  Build image (`docker build`)
    3.  Load image (`minikube image load`)
    4.  Update K8s YAML (`image: new-tag`)
    5.  Apply YAML (`kubectl apply`)
    6.  Test
    ...is the core loop. Getting comfortable with this is essential.
*   **Don't Fear `kubectl describe`:** When things go wrong or you're unsure about the state of a resource, `kubectl describe <resource_type> <name>` is incredibly informative, especially the `Events` section at the bottom.
*   **`kubectl explain` for YAML Deep Dives:** When you're unsure what a field in a YAML does or what options are available, `kubectl explain <resource>.<field>.<subfield>` is your built-in documentation.
*   **Understanding the "Layers":**
    1.  Your App (Python/FastAPI)
    2.  Docker (Containerization: `Dockerfile`, images, containers)
    3.  Kubernetes (Orchestration: Minikube, `kubectl`, YAML manifests for Pods, Deployments, Services, PVCs, ConfigMaps)
    Keep these layers distinct in your mind. Each solves a different set of problems but they build on each other.
*   **Future UI:** Remember our discussion about the UI. What we've built is the backend. A frontend would be a separate application, likely in its own Docker container and Kubernetes Deployment/Service, communicating with this backend over the network via the `simple-splitwise-service`.
*   **Stateful vs. Stateless:** Our application became stateful once we added persistent storage. Many web frontends can be stateless (any replica can serve a request), while backends that manage data are often stateful. Kubernetes has different tools for each (Deployments for stateless, StatefulSets for more complex stateful apps like databases, though we used a Deployment with a PVC for simplicity here).
