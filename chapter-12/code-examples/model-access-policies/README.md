# Model-Access Policies (Chapter 12, Section 12.2)

Sample policies for the model-allowlist control. Each file implements it on
one cloud.

When to use this and why: Chapter 12, Section 12.2 ("Governing model access:
the platform layer").

> **As of November 7, 2026: Bedrock `bedrock-mantle` endpoint.** Bedrock also
> serves models on its `bedrock-mantle` endpoint. There, inference authorizes
> `bedrock-mantle:CreateInference`. The model is named in the
> `bedrock-mantle:Model` condition key instead of a resource ARN. So the AWS
> template has a second statement. It denies that action for every model ID
> outside the allowlist.

| File | Cloud | Mechanism |
|------|-------|-----------|
| `aws-scp-model-allowlist.json` | AWS | Service control policy (or IAM policy) denying `bedrock:InvokeModel` / `bedrock:InvokeModelWithResponseStream` (which also cover Converse and ConverseStream) and `bedrock:CreateModelInvocationJob` (batch inference) for every model except the allowlisted ARNs. A second statement denies `bedrock-mantle:CreateInference` for every model ID outside the allowlist (see the note above). AWS documents this deny-first pattern. Otherwise, model access is enabled by default when the account has AWS Marketplace permissions. |
| `azure-policy-allowed-models.json` | Azure | Assignment of the built-in Azure Policy definition "Azure Machine Learning Deployments should only use approved Registry Models" (`12e5dd16-d201-47ff-849b-8454061c293d`) with `Deny` effect. A deployment of a model outside `allowedAssetIds` fails with an error. |
| `gcp-org-policy-allowed-models.yaml` | Google Cloud | Organization policy for the `vertexai.allowedModels` constraint. Values gate `predict`, `deploy`, and `tune` per model. |

## Before you use these

1. **Replace the placeholder values.** These are templates. Replace model
   IDs, versions, ARNs, and organization IDs with your own allowlist.
   Model identifiers change often.
2. **Check the current provider docs** (model IDs and links as of November 7, 2026):
   - AWS: docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html,
     docs.aws.amazon.com/bedrock/latest/userguide/model-access.html, and
     docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html (the IAM action each inference endpoint authorizes)
   - Azure: learn.microsoft.com/en-us/azure/ai-foundry/how-to/built-in-policy-model-deployment
   - Google Cloud: docs.cloud.google.com/gemini-enterprise-agent-platform/models/control-model-access
3. **Test before you enforce.** On Azure, use `Audit` before `Deny`. On AWS,
   test SCPs in a sandbox OU. A mistyped allowlist locks every agent and
   developer out of inference.
4. **Configure the other controls separately.** Allowlisting is one of four
   controls at this layer. Invocation logging, data residency, and content
   guardrails are set up on their own. For how their settings differ
   between a business solution and developer tooling, see Chapter 12,
   Section 12.2.
