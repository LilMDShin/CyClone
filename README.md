# CyClone
Simulation of a cyclone tracker

## Prerequisites:

- docker
- docker-compose
- Node.js and npm (or yarn)

## Building and Running the Project:

1. **Clone the Repository:**

    ```Bash
    git clone https://github.com/LilMDShin/CyClone.git
    ```

2. **Create the docker network:**

    ```Bash
    sudo docker network create --subnet=192.168.1.0/24 kafka-network
    ```

3. **Handle docker dns config:**
    
    Access the config file:
    ```Bash
    sudo nano /etc/docker/daemon.json
    ```

    Add Google's public dns

    If the "dns" parameter is not in the file then add the following line : "dns": ["8.8.8.8", "8.8.4.4"]
    
    Otherwise, if the options "8.8.8.8", "8.8.4.4" are not specified add them to the existing configuration

    Restart docker:
    ```Bash
    sudo systemctl restart docker
    ```

4. **Build and start containers for the database, api, kafka broker and consumer:**

    Navigate to the CyClone directory

    Build and start containers:
    ```Bash
    sudo docker-compose up --build
    ```

    **If it is the first time building and starting the container then the broker has to be restarted**

    Find the container id of the broker using the following command
    ```Bash
    sudo docker ps -a
    ```

    Restart the broker container:
    ```Bash
    sudo docker restart <container_id>
    ```

5. **Build and start containers for the kafka producers:**

    Open two new terminals for the producers

    Navigate to the directory producer within the kafka directory

    Build and start the container for the first producer:
    ```Bash
    sudo docker-compose -f docker-compose-prod1.yml up --build
    ```

    In another terminal
    Build and start the container for the second producer:
    ```Bash
    sudo docker-compose -f docker-compose-prod2.yml up --build
    ```

6. **Start the frontend:**

    In a new terminal, navigate to the CyClone_front directory

    Install the dependencies:
    ```Bash
    npm install
    ```
   
    Start the development server:
    ```Bash
    npm run dev
    ```

This will typically start a development server at http://localhost:5173/

You can access the frontend application in your web browser