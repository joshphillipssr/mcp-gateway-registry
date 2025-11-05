# ECS MCP Gateway Architecture Diagram - Manual Creation Guide

This document provides a step-by-step guide to manually create the ECS MCP Gateway architecture diagram in draw.io or any diagramming tool.

## Overview

The diagram shows a multi-AZ AWS ECS deployment for the MCP Gateway Registry with separate services for Registry, Authentication (Auth), and Keycloak running in two availability zones (AZ-a and AZ-b).

---

## Quick Reference: All Block Connections

| From Block | To Block | Connection Type | Label | Label Size | Notes |
|-----------|---------|-----------------|-------|-----------|-------|
| Internet Users | Route53 | Arrow | HTTPS | 11pt | External entry point |
| Route53 | Main ALB | Arrow | resolves | 11pt | DNS resolution |
| ACM Certificate | Main ALB | Arrow | certificates | 11pt | HTTPS certificate delivery |
| Main ALB | Registry Task 1 | Arrow | Port 80/443 | 10pt | HTTP/HTTPS routing |
| Main ALB | Registry Task 2 | Arrow | Port 80/443 | 10pt | HTTP/HTTPS routing |
| Main ALB | Registry Task 1 | Arrow | Port 7860 | 10pt | Gradio UI routing |
| Main ALB | Auth Task 1 | Arrow | Port 8888 | 10pt | Auth service routing |
| Main ALB | Auth Task 2 | Arrow | Port 8888 | 10pt | Auth service routing |
| Keycloak ALB | Keycloak Task 1 | Arrow | Port 8080 | 10pt | Keycloak service routing |
| Keycloak ALB | Keycloak Task 2 | Arrow | Port 8080 | 10pt | Keycloak service routing |
| Registry Task 1 | EFS | Arrow | (no label) | — | Shared storage access |
| Registry Task 2 | EFS | Arrow | (no label) | — | Shared storage access |
| Auth Task 1 | EFS | Arrow | (no label) | — | Shared storage access |
| Auth Task 2 | EFS | Arrow | (no label) | — | Shared storage access |
| Keycloak Task 1 | EFS | Arrow | (no label) | — | Shared storage access |
| Keycloak Task 2 | EFS | Arrow | (no label) | — | Shared storage access |
| Keycloak Task 1 | Aurora PostgreSQL | Arrow | (no label) | — | Database access |
| Keycloak Task 2 | Aurora PostgreSQL | Arrow | (no label) | — | Database access |
| Auth Task 1 | Secrets Manager | Arrow | (no label) | — | Credential retrieval |
| Auth Task 2 | Secrets Manager | Arrow | (no label) | — | Credential retrieval |
| Registry Task 1 | Secrets Manager | Arrow | (no label) | — | Credential retrieval |
| Registry Task 2 | Secrets Manager | Arrow | (no label) | — | Credential retrieval |
| Keycloak Task 1 | Secrets Manager | Arrow | (no label) | — | Credential retrieval |
| Keycloak Task 2 | Secrets Manager | Arrow | (no label) | — | Credential retrieval |
| Registry Task 1 | CloudWatch Logs | Arrow | (no label) | — | Container logging |
| Registry Task 2 | CloudWatch Logs | Arrow | (no label) | — | Container logging |
| Auth Task 1 | CloudWatch Logs | Arrow | (no label) | — | Container logging |
| Auth Task 2 | CloudWatch Logs | Arrow | (no label) | — | Container logging |
| Keycloak Task 1 | CloudWatch Logs | Arrow | (no label) | — | Container logging |
| Keycloak Task 2 | CloudWatch Logs | Arrow | (no label) | — | Container logging |
| CloudWatch Logs | CloudWatch Alarms | Arrow | (no label) | — | Metric evaluation |
| CloudWatch Alarms | SNS Topic | Arrow | (no label) | — | Alert notification |

---

## Quick Reference: All Container/Block Colors

| Block Name | Type | Color | RGB Values |
|-----------|------|-------|-----------|
| AWS Account | Container | Light Blue | 173, 216, 230 |
| Security & DNS | Container | Light Grey | 211, 211, 211 |
| AWS Region (us-west-2) | Container | Light Yellow | 255, 255, 224 |
| VPC | Container | Lavender | 230, 230, 250 |
| Public Subnets | Container | Light Cyan | 224, 255, 255 |
| Private Subnets | Container | Misty Rose | 255, 228, 225 |
| AZ-a | Container | Peach Puff | 255, 218, 185 |
| AZ-b | Container | Peach Puff | 255, 218, 185 |
| Storage & Data | Container | Light Green | 144, 238, 144 |
| Monitoring & Alerting | Container | Light Coral | 240, 128, 128 |
| Internet Users | Icon | Standard | — |
| Route53 | AWS Service | Orange | — |
| ACM Certificate | AWS Service | Orange | — |
| Main ALB | AWS Service | Orange | — |
| Keycloak ALB | AWS Service | Orange | — |
| Registry Task 1 & 2 | AWS Service | Light Orange | — |
| Auth Task 1 & 2 | AWS Service | Light Orange | — |
| Keycloak Task 1 & 2 | AWS Service | Light Orange | — |
| EFS Shared Storage | AWS Service | Orange | — |
| Aurora PostgreSQL | AWS Service | Orange | — |
| Secrets Manager | AWS Service | Orange | — |
| CloudWatch Logs | AWS Service | Orange | — |
| CloudWatch Alarms | AWS Service | Orange | — |
| SNS Topic | AWS Service | Orange | — |

---

## Part 1: Container Structure (Create in this order)

### Step 1: Create the outermost container
- **Name**: AWS Account
- **Type**: Container/Cluster
- **Color**: Light Blue (RGB: 173, 216, 230)
- **Purpose**: Contains everything except Internet Users

### Step 2: Inside AWS Account, create "Security & DNS" container
- **Name**: Security & DNS
- **Type**: Container/Cluster
- **Color**: Light Grey (RGB: 211, 211, 211)
- **Position**: Top-left area
- **Parent**: AWS Account

### Step 3: Inside AWS Account, create "AWS Region" container
- **Name**: AWS Region (us-west-2)
- **Type**: Container/Cluster
- **Color**: Light Yellow (RGB: 255, 255, 224)
- **Position**: Center, below Security & DNS
- **Parent**: AWS Account

### Step 4: Inside "AWS Region", create "VPC" container
- **Name**: VPC
- **Type**: Container/Cluster
- **Color**: Lavender (RGB: 230, 230, 250)
- **Parent**: AWS Region

### Step 5: Inside "VPC", create "Public Subnets" container
- **Name**: Public Subnets
- **Type**: Container/Cluster
- **Color**: Light Cyan (RGB: 224, 255, 255)
- **Position**: Top of VPC
- **Parent**: VPC

### Step 6: Inside "VPC", create "Private Subnets" container
- **Name**: Private Subnets
- **Type**: Container/Cluster
- **Color**: Misty Rose (RGB: 255, 228, 225)
- **Position**: Middle of VPC, below Public Subnets
- **Parent**: VPC

### Step 7: Inside "Private Subnets", create "AZ-a" container
- **Name**: AZ-a
- **Type**: Container/Cluster
- **Color**: Peach Puff (RGB: 255, 218, 185)
- **Position**: Left side of Private Subnets
- **Parent**: Private Subnets

### Step 8: Inside "Private Subnets", create "AZ-b" container
- **Name**: AZ-b
- **Type**: Container/Cluster
- **Color**: Peach Puff (RGB: 255, 218, 185)
- **Position**: Right side of Private Subnets
- **Parent**: Private Subnets

### Step 9: Inside "VPC", create "Storage & Data" container
- **Name**: Storage & Data
- **Type**: Container/Cluster
- **Color**: Light Green (RGB: 144, 238, 144)
- **Position**: Bottom-left of VPC
- **Parent**: VPC

### Step 10: Inside "VPC", create "Monitoring & Alerting" container
- **Name**: Monitoring & Alerting
- **Type**: Container/Cluster
- **Color**: Light Coral (RGB: 240, 128, 128)
- **Position**: Bottom-right of VPC
- **Parent**: VPC

---

## Part 2: Network Components

### Step 11: Create "Internet Users" block (OUTSIDE AWS Account)
- **Name**: Internet Users
- **Type**: Mobile/Device icon
- **Position**: Top, outside and above the AWS Account
- **Color**: Any standard icon color

### Step 12: Inside "Security & DNS", create "Route53" block
- **Name**: Route53
- **Subtitle**: mcp-gateway.example.com
- **Type**: AWS Route53 icon (or rectangle)
- **Color**: Orange or Route53 color
- **Parent**: Security & DNS

### Step 13: Inside "Security & DNS", create "ACM Certificate" block
- **Name**: ACM Certificate
- **Subtitle**: HTTPS
- **Type**: AWS Certificate Manager icon (or rectangle)
- **Color**: Orange or ACM color
- **Parent**: Security & DNS

### Step 14: Inside "Public Subnets", create "Main ALB" block
- **Name**: Main ALB
- **Subtitle**: Internet-facing
- **Type**: AWS Elastic Load Balancer icon
- **Color**: Orange or ELB color
- **Parent**: Public Subnets

### Step 15: Inside "Public Subnets", create "Keycloak ALB" block
- **Name**: Keycloak ALB
- **Subtitle**: Private
- **Type**: AWS Elastic Load Balancer icon
- **Color**: Orange or ELB color
- **Parent**: Public Subnets

---

## Part 3: ECS Fargate Tasks

### Step 16: Inside "AZ-a", create three Fargate tasks (stacked vertically)
1. **Registry Task 1**
   - Name: Registry Task 1
   - Type: AWS Fargate icon
   - Color: Light orange or compute color

2. **Auth Task 1**
   - Name: Auth Task 1
   - Type: AWS Fargate icon
   - Color: Light orange or compute color

3. **Keycloak Task 1**
   - Name: Keycloak Task 1
   - Type: AWS Fargate icon
   - Color: Light orange or compute color

### Step 17: Inside "AZ-b", create three Fargate tasks (mirror of AZ-a)
1. **Registry Task 2**
   - Name: Registry Task 2
   - Type: AWS Fargate icon
   - Color: Light orange or compute color

2. **Auth Task 2**
   - Name: Auth Task 2
   - Type: AWS Fargate icon
   - Color: Light orange or compute color

3. **Keycloak Task 2**
   - Name: Keycloak Task 2
   - Type: AWS Fargate icon
   - Color: Light orange or compute color

---

## Part 4: Storage and Data Components

### Step 18: Inside "Storage & Data", create "EFS Shared Storage" block
- **Name**: EFS Shared Storage
- **Subtitle**: /servers /models /logs
- **Type**: AWS EFS icon
- **Color**: Orange or EFS color

### Step 19: Inside "Storage & Data", create "Aurora PostgreSQL" block
- **Name**: Aurora PostgreSQL
- **Subtitle**: Serverless v2
- **Type**: AWS Aurora icon
- **Color**: Orange or database color

### Step 20: Inside "Storage & Data", create "Secrets Manager" block
- **Name**: Secrets Manager
- **Subtitle**: Encryption: KMS
- **Type**: AWS Secrets Manager icon
- **Color**: Orange or security color

---

## Part 5: Monitoring Components

### Step 21: Inside "Monitoring & Alerting", create "CloudWatch Logs" block
- **Name**: CloudWatch Logs
- **Subtitle**: Container Insights
- **Type**: AWS CloudWatch icon
- **Color**: Orange or management color

### Step 22: Inside "Monitoring & Alerting", create "CloudWatch Alarms" block
- **Name**: CloudWatch Alarms
- **Type**: AWS CloudWatch icon
- **Color**: Orange or management color

### Step 23: Inside "Monitoring & Alerting", create "SNS Topic" block
- **Name**: SNS Topic
- **Subtitle**: slack/email/sms
- **Type**: AWS SNS icon
- **Color**: Orange or integration color

---

## Part 6: Arrow Connections (Create in this order)

### External to DNS Section
1. **Internet Users → Route53**
   - Arrow Type: Straight line with arrowhead pointing right
   - Label: "HTTPS"
   - Label Position: On arrow
   - Label Font Size: 11pt

2. **Route53 → Main ALB**
   - Arrow Type: Straight line with arrowhead pointing right
   - Label: "resolves"
   - Label Position: On arrow
   - Label Font Size: 11pt

3. **ACM Certificate → Main ALB**
   - Arrow Type: Straight line with arrowhead pointing right
   - Label: "certificates"
   - Label Position: On arrow
   - Label Font Size: 11pt

### Main ALB to ECS Tasks (Port-based routing)
4. **Main ALB → Registry Task 1**
   - Arrow Type: Straight line with arrowhead
   - Label: "Port 80/443"
   - Label Font Size: 10pt

5. **Main ALB → Registry Task 2**
   - Arrow Type: Straight line with arrowhead
   - Label: "Port 80/443"
   - Label Font Size: 10pt

6. **Main ALB → Registry Task 1** (Second connection)
   - Arrow Type: Straight line with arrowhead (curved to avoid overlap)
   - Label: "Port 7860"
   - Label Font Size: 10pt

7. **Main ALB → Auth Task 1**
   - Arrow Type: Straight line with arrowhead
   - Label: "Port 8888"
   - Label Font Size: 10pt

8. **Main ALB → Auth Task 2**
   - Arrow Type: Straight line with arrowhead
   - Label: "Port 8888"
   - Label Font Size: 10pt

### Keycloak ALB to Keycloak Tasks
9. **Keycloak ALB → Keycloak Task 1**
   - Arrow Type: Straight line with arrowhead
   - Label: "Port 8080"
   - Label Font Size: 10pt

10. **Keycloak ALB → Keycloak Task 2**
    - Arrow Type: Straight line with arrowhead
    - Label: "Port 8080"
    - Label Font Size: 10pt

### ECS Tasks to EFS (No labels for cleaner diagram)
11. **Registry Task 1 → EFS**
    - Arrow Type: Straight line with arrowhead
    - No label

12. **Registry Task 2 → EFS**
    - Arrow Type: Straight line with arrowhead
    - No label

13. **Auth Task 1 → EFS**
    - Arrow Type: Straight line with arrowhead
    - No label

14. **Auth Task 2 → EFS**
    - Arrow Type: Straight line with arrowhead
    - No label

15. **Keycloak Task 1 → EFS**
    - Arrow Type: Straight line with arrowhead
    - No label

16. **Keycloak Task 2 → EFS**
    - Arrow Type: Straight line with arrowhead
    - No label

### Keycloak Tasks to Aurora (Database access)
17. **Keycloak Task 1 → Aurora PostgreSQL**
    - Arrow Type: Straight line with arrowhead
    - No label

18. **Keycloak Task 2 → Aurora PostgreSQL**
    - Arrow Type: Straight line with arrowhead
    - No label

### All Tasks to Secrets Manager (Credential retrieval)
19. **Auth Task 1 → Secrets Manager**
    - Arrow Type: Straight line with arrowhead
    - No label

20. **Auth Task 2 → Secrets Manager**
    - Arrow Type: Straight line with arrowhead
    - No label

21. **Registry Task 1 → Secrets Manager**
    - Arrow Type: Straight line with arrowhead
    - No label

22. **Registry Task 2 → Secrets Manager**
    - Arrow Type: Straight line with arrowhead
    - No label

23. **Keycloak Task 1 → Secrets Manager**
    - Arrow Type: Straight line with arrowhead
    - No label

24. **Keycloak Task 2 → Secrets Manager**
    - Arrow Type: Straight line with arrowhead
    - No label

### All Tasks to CloudWatch Logs (Logging)
25. **Registry Task 1 → CloudWatch Logs**
    - Arrow Type: Straight line with arrowhead
    - No label

26. **Registry Task 2 → CloudWatch Logs**
    - Arrow Type: Straight line with arrowhead
    - No label

27. **Auth Task 1 → CloudWatch Logs**
    - Arrow Type: Straight line with arrowhead
    - No label

28. **Auth Task 2 → CloudWatch Logs**
    - Arrow Type: Straight line with arrowhead
    - No label

29. **Keycloak Task 1 → CloudWatch Logs**
    - Arrow Type: Straight line with arrowhead
    - No label

30. **Keycloak Task 2 → CloudWatch Logs**
    - Arrow Type: Straight line with arrowhead
    - No label

### Monitoring Pipeline
31. **CloudWatch Logs → CloudWatch Alarms**
    - Arrow Type: Straight line with arrowhead
    - No label

32. **CloudWatch Alarms → SNS Topic**
    - Arrow Type: Straight line with arrowhead
    - No label

---

## Summary of Blocks and Components

| Block Name | AWS Service | Purpose | Color |
|-----------|-----------|---------|-------|
| Internet Users | External | End users accessing the system | Standard icon |
| Route53 | AWS Route53 | DNS resolution for domain | Orange |
| ACM Certificate | AWS Certificate Manager | HTTPS certificate management | Orange |
| Main ALB | AWS Elastic Load Balancer | Routes external traffic to services | Orange |
| Keycloak ALB | AWS Elastic Load Balancer | Internal routing for auth service | Orange |
| Registry Task 1 & 2 | AWS ECS Fargate | Agent registry service (2 instances) | Light Orange |
| Auth Task 1 & 2 | AWS ECS Fargate | Authentication service (2 instances) | Light Orange |
| Keycloak Task 1 & 2 | AWS ECS Fargate | Identity provider service (2 instances) | Light Orange |
| EFS Shared Storage | AWS EFS | Shared file system for all services | Light Green |
| Aurora PostgreSQL | AWS Aurora | Database for Keycloak | Light Green |
| Secrets Manager | AWS Secrets Manager | Credential and encryption key storage | Light Green |
| CloudWatch Logs | AWS CloudWatch | Centralized logging for all tasks | Light Coral |
| CloudWatch Alarms | AWS CloudWatch | Alert conditions based on metrics | Light Coral |
| SNS Topic | AWS SNS | Notification delivery (Slack/Email/SMS) | Light Coral |

---

## Key Architecture Principles

1. **Multi-AZ Deployment**: Both Registry, Auth, and Keycloak services run in two availability zones (AZ-a and AZ-b) for high availability and fault tolerance.

2. **Load Balancing**: Main ALB handles external traffic to Registry and Auth services, while Keycloak ALB handles internal auth traffic.

3. **Port Mapping**:
   - Registry: 80/443 (HTTP/HTTPS) and 7860 (Gradio interface)
   - Auth: 8888
   - Keycloak: 8080

4. **Shared Storage**: All tasks access the same EFS volume with mount points at /servers, /models, and /logs.

5. **Security**: Credentials managed through Secrets Manager with KMS encryption.

6. **Monitoring**: All tasks log to CloudWatch, which triggers alarms that send notifications via SNS.

---

## Tips for draw.io Creation

- Use the AWS shape library in draw.io for authentic AWS icons
- Align containers with proper nesting to show hierarchy
- Use different colors for visual distinction between logical groups
- Keep labels on arrows short and positioned clearly
- Add spacing between components for clarity
- Test the hierarchy by clicking on containers to verify nesting
