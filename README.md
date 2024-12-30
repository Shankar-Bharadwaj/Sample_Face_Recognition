# A. Flask Application Deployment on AWS EC2

This guide outlines the steps to deploy a Flask application on an AWS EC2 instance with Gunicorn and Nginx.

## Step 1: Build a Python Web App using Flask

1. Create a Flask application in your local machine and add the required dependencies to `requirements.txt`.
2. Test the app locally,
```
python3 app.py
```

## Step 2: Create an EC2 instance on AWS

To deploy your Flask application, you need to create an EC2 instance on AWS.

1. **Choose an Amazon Machine Image (AMI)**
   - The AMI is the basic unit of deployment and determines the operating system and software pre-installed on the instance.
   - You could select one of the following AMIs: Amazon Linux, macOS, Ubuntu, Windows, Red Hat, and many more.
   - This guide uses **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type, 64-bit (x86)** as the chosen AMI.
2. **Choose an Instance Type**
   - Instance types define the hardware resources allocated to your instance, such as CPU and memory.
   - For testing and light workloads, choose **t2.micro** or **t3.micro** (eligible for the AWS Free Tier).
   - For production, select an instance type based on your application's performance requirements.
3. **Generate a Key Pair for login**
   - Key pairs provide secure SSH access to your instance.
   - Create a new key pair if you don't already have one and download the `.pem` file. Store it securely as this is required to connect with your instance.
4. **Configure Network Settings**
   - **VPC and Subnet**: Use the default VPC and choose a subnet based on your region.
   - **Security Group**: You can either create a new security group or use an existing security group. Ensure that it has the required inbound and outbound rules for your app.
5. **Configure Storage**
   - Adjust the size of the storage based on your application's needs.

## Step 3: Connect to the EC2 instance

1. Before connecting to the EC2 instance, change the permissions of the `.pem` file to be only read by the owner,
```
chmod 400 path/to/key.pem
```
2. Use SSH to connect to your EC2 instance,
```
ssh -i <your-key.pem> ubuntu@<your-ec2-public-ip>
```

***WinSCP and PuTTY is not required for Linux/MacOS users.***

## Step 4: Transfer Required Files

1. Before transferring the application, modify the Flask app's code to allow it to listen on all network interfaces,
\
\
Replace:
```
app.run(debug=True) 
```
&emsp;&emsp;With:
```
app.run(host='0.0.0.0', port=5000)
```

2. Use the `scp` command to securely copy your application files to the EC2 instance,
```
scp -i <your-key.pem> -r /path/to/your-app ubuntu@<your-ec2-public-ip>:/home/ubuntu/
```

3. Once the files are transferred, log in to your EC2 instance and navigate to the application's directory,
```
cd /home/ubuntu/your-app
```

## Step 5: Install Required Libraries and Test Your App

1. Update the system and install necessary tools:
```
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv -y
```

2. Set up a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

4. Test the app:
```
python3 app.py
```

5. Visit `http://<your-ec2-public-ip>:5000` to ensure the app is running.

## Step 6: Set Up the App for Production

Flask’s built-in development server is not suitable for production use as it is not designed to handle multiple concurrent requests efficiently. To set up a production-ready environment, we use two key components:

1. **Web Server (Nginx)**
   - A web server like **Nginx** acts as a reverse proxy, handling incoming requests from the internet.
   - It can manage multiple simultaneous connections, serve static files efficiently, and distribute traffic to your Flask app.
   - Nginx ensures that requests are quickly handled and improves the overall **scalability** and **security** of your application.
\
\
**Install Nginx**
```
sudo apt install nginx -y
```
![Flow of request and responses in a production-level architecture of a web application.](https://github.com/Shankar-Bharadwaj/Sample_Face_Recognition/blob/master/images-readme/Nginx-Gunicorn.png)
2. **WSGI Server (Gunicorn)**
   - A **WSGI (Web Server Gateway Interface)** server ensures portability between web servers and Python web frameworks.
   - Gunicorn is a lightweight WSGI server that processes requests forwarded by Nginx and passes them to our Flask application.
\
\
**Install Gunicorn**
```
pip install gunicorn
```
![WSGI involvement in the architecture](https://github.com/Shankar-Bharadwaj/Sample_Face_Recognition/blob/master/images-readme/Nginx-Gunicorn-2.png)

3. **Integrate Nginx with Gunicorn**
   - Nginx acts as a reverse proxy, forwarding incoming requests to Gunicorn.
   - Create an Nginx Configuration File,
```
sudo nano /etc/nginx/sites-available/flask_app
```
Add the following configuration in the above file (replace `<EC2-Public-IP>` with your instance's public IP),
```
server {
    listen 80;
    server_name <EC2-Public-IP>;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the Configuration and Restart Nginx
```
sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
4. Run Gunicorn
Start the Gunicorn server to serve your Flask app:
```
gunicorn --bind 0.0.0.0:5000 app:app
```

Your application is now production-ready and accessible via your EC2 instance's public IP on port 80, that is, `http://<EC2-Public-IP>/`.
<br />
<br />

# B. Flask Application Deployment on AWS ECS Fargate

This guide outlines the steps to deploy a Flask application on **AWS ECS (Elastic Container Service) Fargate.**

## Step 1: Build a Python Web App using Flask

1. Create a Flask application in your local machine and add the required dependencies to `requirements.txt`.
2. Test the app locally,
```
python3 app.py
```

## Step 2: Dockerize the Application

1. Create a `Dockerfile` to containerize the application.
2. The `Dockerfile` includes information such as the base images, requirements.txt, application code, appropriate ports, and the command to run the application.
3. Install **Docker desktop** on your local machine to access the Docker CLI and build the Docker Image using the following command,
```
docker build -t image-name .
```
4. Push the Image to Docker Hub using,
```
docker push profile_username/image-name
```

## Step 3: Set Up AWS ECS Fargate

1. Create ECS Cluster
   - Navigate to the ECS dashboard in AWS Console.
   - Create a new cluster for the project.
2. Define Task Definition
   - Provide key configuration details like Task CPU, Task Memory, Docker Image (profile_username/image-name), Port Mappings (for eg., 8080:8080), App protocol (for eg., HTTP).
3. Create Security Groups
   - Create a security group to allow specific inbound and outbound traffic according to the purpose of your application.

## Step 4: Create an ECS Fargate Service

1. Create an ECS service within the cluster with **'Fargate'** as the launch type and the task definition as the task family defined above.
2. Specify the number of instances to be created of your container under **Desired tasks**.
3. After successful creation, the service is deployed. The ECS Fargate service is set up with the image from Docker Hub.

## Step 5: Test the Deployment

1. Verify the task is running
   - Check if the task is running properly in the ECS console under the **'Tasks'** tab.
2. Open the Application
   - Once the task is running, you can access the application in the browser using `http://<public-ip>:8080`.

## Common Errors and Troubleshooting

1. **Error:"The sum of the container CPU must not exceed the task CPU"**
   - This occurs when the sum of allocated vCPU for containers exceeds the vCPU for the task.
   - Adjust the container CPU to be less than or equal to the task CPU.
2. **Error: "Error occurred during operation 'CreateCluster SDK error: Service Unavailable"**
   - This can happen due to temporary issues with AWS services.
   - Retry the operation after some time.
3. **Error: "CannotPullContainerError: Image manifest does not contain descriptor matching platform"**
   - The error indicates that the ECS instance cannot pull the image due to mismatched architecture.
   - Ensure the image architecture matches the ECS task's configuration. The image's architecture can be viewed under 'Tags' in Docker Hub.
