#!/usr/bin/env python3
"""
ECS MCP Gateway Architecture Diagram
Generates AWS architecture diagram using mingrammer/diagrams
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import (
    Route53,
    ELB,
)
from diagrams.aws.compute import (
    ECS,
    Fargate,
)
from diagrams.aws.storage import (
    EFS,
)
from diagrams.aws.database import (
    Aurora,
)
from diagrams.aws.security import (
    SecretsManager,
    CertificateManager,
)
from diagrams.aws.management import (
    Cloudwatch,
)
from diagrams.aws.integration import (
    SimpleNotificationServiceSns as SNS,
)
from diagrams.generic.os import Ubuntu
from diagrams.generic.device import Mobile


def create_ecs_diagram():
    """Create ECS MCP Gateway architecture diagram"""

    with Diagram(
        "ECS MCP Gateway Architecture",
        filename="/home/ubuntu/repos/mcp-gateway-registry/docs/diagrams/ecs-deployment-architecture",
        show=False,
        direction="TB",
        outformat="png",
        graph_attr={
            "rankdir": "TB",
            "nodesep": "1.2",
            "ranksep": "1.5",
            "edge": '["fontsize"="9", "fontname"="arial"]',
            "concentrate": "false",
        }
    ):

        # External Users (outside AWS)
        users = Mobile("Internet Users")

        # AWS Account - Everything else inside
        with Cluster("AWS Account", graph_attr={"style": "filled", "color": "lightblue"}):

            # DNS & Security
            with Cluster("Security & DNS", graph_attr={"style": "filled", "color": "lightgrey"}):
                dns = Route53("Route53\nmcp-gateway.example.com")
                acm = CertificateManager("ACM Certificate\nHTTPS")

            with Cluster("AWS Region (us-west-2)", graph_attr={"style": "filled", "color": "lightyellow"}):
                with Cluster("VPC", graph_attr={"style": "filled", "color": "lavender"}):

                    # Load Balancers
                    with Cluster("Public Subnets", graph_attr={"style": "filled", "color": "lightcyan"}):
                        main_alb = ELB("Main ALB\nInternet-facing")
                        keycloak_alb = ELB("Keycloak ALB\nPrivate")

                    # ECS Services - Wider AZ layout with more spacing
                    with Cluster("Private Subnets", graph_attr={"style": "filled", "color": "mistyrose"}):

                        with Cluster("AZ-a", graph_attr={"style": "filled", "color": "peachpuff", "nodesep": "0.8", "ranksep": "1.2"}):
                            registry_task_1 = Fargate("Registry\nTask 1")
                            auth_task_1 = Fargate("Auth\nTask 1")
                            keycloak_task_1 = Fargate("Keycloak\nTask 1")

                        with Cluster("AZ-b", graph_attr={"style": "filled", "color": "peachpuff", "nodesep": "0.8", "ranksep": "1.2"}):
                            registry_task_2 = Fargate("Registry\nTask 2")
                            auth_task_2 = Fargate("Auth\nTask 2")
                            keycloak_task_2 = Fargate("Keycloak\nTask 2")

                    # Storage & Data
                    with Cluster("Storage & Data", graph_attr={"style": "filled", "color": "lightgreen"}):
                        efs = EFS("EFS Shared Storage\n/servers /models /logs")
                        aurora = Aurora("Aurora PostgreSQL\nServerless v2")
                        secrets = SecretsManager("Secrets Manager\nEncryption: KMS")

                    # Monitoring (inside AWS but at the bottom)
                    with Cluster("Monitoring & Alerting", graph_attr={"style": "filled", "color": "lightcoral"}):
                        cloudwatch = Cloudwatch("CloudWatch Logs\nContainer Insights")
                        alarms = Cloudwatch("CloudWatch Alarms")
                        sns = SNS("SNS Topic\nslack/email/sms")

        # Connections - Users to DNS
        users >> Edge(label="HTTPS", fontsize="11", fontname="arial") >> dns
        dns >> Edge(label="resolves", fontsize="11", fontname="arial") >> main_alb
        acm >> Edge(label="certificates", fontsize="11", fontname="arial") >> main_alb

        # Main ALB to Services (via Target Groups)
        main_alb >> Edge(label="Port 80/443", fontsize="10", fontname="arial") >> registry_task_1
        main_alb >> Edge(label="Port 80/443", fontsize="10", fontname="arial") >> registry_task_2
        main_alb >> Edge(label="Port 7860", fontsize="10", fontname="arial") >> registry_task_1
        main_alb >> Edge(label="Port 8888", fontsize="10", fontname="arial") >> auth_task_1
        main_alb >> Edge(label="Port 8888", fontsize="10", fontname="arial") >> auth_task_2

        # Keycloak ALB
        keycloak_alb >> Edge(label="Port 8080", fontsize="10", fontname="arial") >> keycloak_task_1
        keycloak_alb >> Edge(label="Port 8080", fontsize="10", fontname="arial") >> keycloak_task_2

        # Service to EFS (no labels - cleaner)
        registry_task_1 >> efs
        registry_task_2 >> efs
        auth_task_1 >> efs
        auth_task_2 >> efs
        keycloak_task_1 >> efs
        keycloak_task_2 >> efs

        # Keycloak to Aurora (no labels - cleaner)
        keycloak_task_1 >> aurora
        keycloak_task_2 >> aurora

        # Services to Secrets Manager (no labels - cleaner)
        auth_task_1 >> secrets
        auth_task_2 >> secrets
        registry_task_1 >> secrets
        registry_task_2 >> secrets
        keycloak_task_1 >> secrets
        keycloak_task_2 >> secrets

        # Services to CloudWatch (no labels - cleaner)
        registry_task_1 >> cloudwatch
        registry_task_2 >> cloudwatch
        auth_task_1 >> cloudwatch
        auth_task_2 >> cloudwatch
        keycloak_task_1 >> cloudwatch
        keycloak_task_2 >> cloudwatch

        # CloudWatch to Alarms to SNS (no labels - cleaner)
        cloudwatch >> alarms
        alarms >> sns


if __name__ == "__main__":
    create_ecs_diagram()
    print("✅ ECS deployment architecture diagram generated successfully!")
    print("📊 Output: /home/ubuntu/repos/mcp-gateway-registry/docs/diagrams/ecs-deployment-architecture.png")
