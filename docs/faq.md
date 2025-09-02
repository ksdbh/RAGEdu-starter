# FAQ

Q: Can I run this without AWS?
A: Yes. The scaffold includes mocks and stubs (MockCognitoClient, StubEmbeddings, in-memory DB). Set USE_IN_MEMORY_DB=1.

Q: How do I switch to real OpenSearch or Bedrock?
A: Provide proper AWS credentials and update the adapter implementations. See docs/aws/integrations.md and infra/.

Where to edit

!!! info "Where to edit"
- FAQ: docs/faq.md
