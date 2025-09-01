// OpenSearch Serverless collection (vector / kNN-ready in future)
resource "aws_opensearchserverless_collection" "vec" {
  name = var.collection_name
  type = "SEARCH"

  // Additional configuration (capacity, network, security) should be added for production
}
