#Semantic Retrieval Gemini

import time
service_account_file_name = 'service_account_key.json'

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(service_account_file_name)

scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])


import google.ai.generativelanguage as glm
generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)

corpus_resource_name = "corpora/chroniclingamericatext-o3r7dekmxzmt"

#name: "corpora/chroniclingamericatext-o3r7dekmxzmt"
#display_name: "Chronicling_America_Text"
#create_time {
#  seconds: 1738264032
#  nanos: 262192000
#}
#update_time {
#  seconds: 1738264032
#  nanos: 262192000
#}

# Create a document with a custom display name.
example_document = glm.Document(display_name="01011925")

# Add metadata.
# Metadata also supports numeric values not specified here
document_metadata = [
    glm.CustomMetadata(key="date", numeric_value = 19250101)]
example_document.custom_metadata.extend(document_metadata)

# Make the request
# corpus_resource_name is a variable set in the "Create a corpus" section.
create_document_request = glm.CreateDocumentRequest(parent=corpus_resource_name, document=example_document)
create_document_response = retriever_service_client.create_document(create_document_request)

# Set the `document_resource_name` for subsequent sections.
document_resource_name = create_document_response.name
print(create_document_response)

document_resource_name = "corpora/chroniclingamericatext-o3r7dekmxzmt/documents/01011925-cae4xw51jijj"

#%pip install -qU langchain-text-splitters

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load example document
with open("/Users/capricecarstensen/Documents/Github/Chronicling_America_Data/Test/search_results_01_01_1925.txt") as f:
    news_articles = f.read()

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=1000,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)
passages = text_splitter.create_documents([news_articles])

first_x_items = passages[101:1000] 

# After loading passages, process in batches of 100
batch_size = 100
total_passages = len(passages)

for i in range(0, total_passages, batch_size):
    batch_end = min(i + batch_size, total_passages)
    current_batch = passages[i:batch_end]
    
    chunks = []
    for passage in current_batch:
        chunk = glm.Chunk(data={'string_value': passage.page_content})
        chunk.custom_metadata.append(glm.CustomMetadata(key = "publish_date", numeric_value = 19250101))
        chunks.append(chunk)
    
    # Make the request for this batch
    create_chunk_requests = []
    for chunk in chunks:
        create_chunk_requests.append(glm.CreateChunkRequest(parent=document_resource_name, chunk=chunk))
    
    request = glm.BatchCreateChunksRequest(parent=document_resource_name, requests=create_chunk_requests)
    payload_size = len(create_chunk_requests)
    print(f"Processing batch {i//batch_size + 1}, size: {payload_size} chunks")
    
    response = retriever_service_client.batch_create_chunks(request)
    print(f"Completed batch {i//batch_size + 1}")
    
    # Add a small delay between batches
    if batch_end < total_passages:
        time.sleep(1)

'''
#check chunks
request = glm.ListChunksRequest(parent=document_resource_name)
list_chunks_response = retriever_service_client.list_chunks(request)
for index, chunks in enumerate(list_chunks_response.chunks):
  print(f'\nChunk # {index + 1}')
  print(f'Resource Name: {chunks.name}')
  # Only ACTIVE chunks can be queried.
  print(f'State: {glm.Chunk.State(chunks.state).name}')
'''

