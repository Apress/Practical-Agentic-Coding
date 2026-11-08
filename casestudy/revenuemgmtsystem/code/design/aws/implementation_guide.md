# AWS Implementation Guide: ZenithStays Platform

> **Note (as of November 7, 2026):** This is the deployment plan from the design phase (December 2025), not a tested runbook. The four stacks it describes are not in this repository. The App stack expects a backend Dockerfile and a `src/lambdas/marketWorker.ts`, and the repository includes neither. The CDK imports, the DynamoDB properties, the knowledge base storage block, and the model references below match the current services. The rest is kept as written. Amazon Bedrock Agents, which AWS calls Bedrock Agents Classic, is closed to new customers (from July 30, 2026). AWS recommends Amazon Bedrock AgentCore for new agent work. See [Amazon Bedrock Agents Classic maintenance mode](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-classic-maintenance-mode.html).

## 1. Overview
This guide provides step-by-step instructions to deploy the ZenithStays Cloud Architecture on AWS.
We use **AWS CDK (Cloud Development Kit)** with TypeScript for Infrastructure as Code (IaC). This allows us to define our infrastructure using the same language as our application.

### 1.1 Prerequisites
*   AWS CLI installed & configured.
*   Node.js v20+ installed.
*   AWS CDK Toolkit installed: `npm install -g aws-cdk`

---

## 2. Infrastructure Stack (CDK)

We will define four primary stacks:
1.  **Core Stack**: VPC, Networks, Security Groups.
2.  **Data Stack**: DynamoDB Tables, S3 Buckets.
3.  **App Stack**: Fargate Service, API Gateway, Lambda Functions.
4.  **AI Stack**: Bedrock Agents (using Custom Resources where L2 constructs are missing).

### 2.1 Project Initialization
```bash
mkdir infrastructure && cd infrastructure
cdk init app --language typescript
```

`cdk init` installs `aws-cdk-lib`. In CDK v2 the DynamoDB, ECS, ECS patterns, API Gateway v2, and Lambda Node.js construct libraries ship inside it, so no extra packages are needed. The separate `@aws-cdk/aws-*` packages are the CDK v1 libraries.

### 2.2 Data Layer (DynamoDB)
File: `lib/data-stack.ts`
```typescript
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class DataStack extends cdk.Stack {
  public readonly table: dynamodb.Table;

  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.table = new dynamodb.Table(this, 'ZenithTable', {
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: true },
    });
    
    // Add Global Secondary Indexes (GSI) for access patterns
    this.table.addGlobalSecondaryIndex({
      indexName: 'GSI1',
      partitionKey: { name: 'gsi1pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'gsi1sk', type: dynamodb.AttributeType.STRING },
    });
  }
}
```

### 2.3 Compute & API Layer (Fargate + API Gateway)
File: `lib/app-stack.ts`
```typescript
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecsp from 'aws-cdk-lib/aws-ecs-patterns';
import * as apigw from 'aws-cdk-lib/aws-apigatewayv2';
import { HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as lambda from 'aws-cdk-lib/aws-lambda-nodejs';

// ... imports for cdk and the VPC props

export class AppStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: AppStackProps) {
    super(scope, id, props);

    // 1. Fargate Service (Core API)
    const cluster = new ecs.Cluster(this, 'ZenithCluster', { vpc: props.vpc });
    
    const fargateService = new ecsp.ApplicationLoadBalancedFargateService(this, 'ApiService', {
      cluster,
      memoryLimitMiB: 1024,
      cpu: 512,
      taskImageOptions: {
        image: ecs.ContainerImage.fromAsset('../backend'),
        environment: {
          TABLE_NAME: props.table.tableName,
          AWS_REGION: this.region
        },
      },
    });

    // 2. Market Data Worker (Lambda)
    const marketWorker = new lambda.NodejsFunction(this, 'MarketWorker', {
      entry: '../backend/src/lambdas/marketWorker.ts',
      timeout: cdk.Duration.seconds(30),
      environment: {
        TABLE_NAME: props.table.tableName
      }
    });

    props.table.grantReadWriteData(marketWorker);
  }
}
```

### 2.4 Agentic AI Layer (Bedrock Agents)
*Note: As of Dec 2025, AWS CDK L2 constructs for Bedrock Agents are evolving. We use `CfnAgent` (L1 Construct).*

File: `lib/ai-stack.ts`
```typescript
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import * as s3 from 'aws-cdk-lib/aws-s3';

export class AiStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: AiStackProps) {
    super(scope, id, props);

    // 1. S3 Bucket for Knowledge Base Docs
    const docsBucket = new s3.Bucket(this, 'RevenueDocsBucket', {
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // 2. Knowledge Base (S3 Vectors as the vector store)
    // We use the L1 CfnKnowledgeBase construct.
    const knowledgeBase = new bedrock.CfnKnowledgeBase(this, 'ZenithKB', {
      name: 'RevenueDocs',
      roleArn: kbRole.roleArn,
      knowledgeBaseConfiguration: {
        type: 'VECTOR',
        vectorKnowledgeBaseConfiguration: {
          embeddingModelArn: 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0',
        }
      },
      storageConfiguration: {
        type: 'S3_VECTORS',
        s3VectorsConfiguration: {
          indexArn: vectorIndexArn, // ARN of an index in an S3 vector bucket
        },
      }
    });

    // 3. Data Source (Linking Bucket to KB)
    new bedrock.CfnDataSource(this, 'DocsDataSource', {
      knowledgeBaseId: knowledgeBase.ref,
      name: 'S3DocsSource',
      dataSourceConfiguration: {
        type: 'S3',
        s3Configuration: {
          bucketArn: docsBucket.bucketArn
        }
      }
    });

    // 4. Define the Agent with KB Association
    const agent = new bedrock.CfnAgent(this, 'StrategyAgent', {
      agentName: 'ZenithStrategyAgent',
      agentResourceRoleArn: agentRole.roleArn,
      foundationModel: agentModelId, // a current high-reasoning Claude model ID from the Bedrock model catalog
      instruction: `You are a Revenue Manager. Use the Code Interpreter for math. 
                   Check the 'RevenueDocs' Knowledge Base for policy questions.
                   Use the 'MarketTools' action group for fetching data.`,
      knowledgeBases: [{
        knowledgeBaseId: knowledgeBase.ref,
        description: "Standard Operating Procedures and Guidelines"
      }],
      actionGroups: [{
        actionGroupName: 'MarketTools',
        actionGroupExecutor: {
          lambda: actionLambda.functionArn // actionLambda defined as before
        },
        apiSchema: {
          payload: marketToolsSchema // the action group's OpenAPI document as a JSON string
        }
      }]
    });
  }
}
```

---

## 3. Deployment Steps

### Step 1: Bootstrap Environment
This sets up the CDK toolkit stack in your AWS account (S3 bucket for assets).
```bash
cd infrastructure
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```

### Step 2: Deploy Stacks
Deploy all stacks in dependency order.
```bash
cdk deploy --all
```

### Step 3: Post-Deployment Config
1.  **Agent Alias**: Go to Bedrock Console, create an Alias for the deployed Agent.
2.  **Environment Variables**: Copy the `AgentId` and `TableArn` outputs.
3.  **Update Secrets**: Store API Keys (PredictHQ, etc.) in AWS Secrets Manager.

---

## 4. Monitoring & Observability
*   **CloudWatch Logs**: Enabled for all Fargate Tasks and Lambda Functions.
*   **X-Ray Tracing**: Enabled on API Gateway and Lambda to trace requests end-to-end.
*   **Bedrock Model Invocation Logging**: Configured to log prompts/completions to S3 for audit (PII redacted).
