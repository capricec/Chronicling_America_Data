#Semantic Retrieval Gemini

##NEED TO UPDATE THIS TO CHUNK AT 'URL' AND SAVE IN METADATA? WANT TO BE ABLE TO CITE THE URL IN APP


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

document_resource_name = "corpora/chroniclingamericatext-o3r7dekmxzmt/documents/01011925-fn5whlh1xyst"

#delete old documents
#req = glm.DeleteDocumentRequest(name=document_resource_name, force=True)
#delete_corpus_response = retriever_service_client.delete_document(req)
#print("Successfully deleted corpus: " + document_resource_name)

# Create a document with a custom display name.
#example_document = glm.Document(display_name="01011925")

# Add metadata.
# Metadata also supports numeric values not specified here

#document_metadata = [
#    glm.CustomMetadata(key="date", numeric_value = 19250101)]
#example_document.custom_metadata.extend(document_metadata)

# Make the request
# corpus_resource_name is a variable set in the "Create a corpus" section.
#create_document_request = glm.CreateDocumentRequest(parent=corpus_resource_name, document=example_document)
#create_document_response = retriever_service_client.create_document(create_document_request)

# Set the `document_resource_name` for subsequent sections.
#document_resource_name = create_document_response.name
#print(create_document_response)



#%pip install -qU langchain-text-splitters

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load and split document by articles first
def split_into_articles(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split the content at "Title:" but keep the delimiter
    articles = content.split("\nTitle:")
    # Add "Title:" back to all articles except the first one (if it started with Title:)
    articles = [articles[0]] + [f"Title:{article}" for article in articles[1:]]
    return [article.strip() for article in articles if article.strip()]

# Load example document
file_path = "/Users/capricecarstensen/Documents/Github/Chronicling_America_Data/Test/search_results_01_01_1925.txt"
articles = split_into_articles(file_path)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)

def extract_url(article_text):
    """Extract URL from article text"""
    lines = article_text.split('\n')
    for line in lines:
        if line.startswith('URL:'):
            return line.replace('URL:', '').strip()
    return None

# Process each article separately
all_passages = []
for article in articles:
    article_chunks = text_splitter.create_documents([article])
    url = extract_url(article)  # Get URL for this article
    for chunk in article_chunks:
        chunk.metadata = {'url': url}  # Change to dictionary format
    all_passages.extend(article_chunks)

# After loading passages, process in batches of 100
batch_size = 100
total_passages = len(all_passages)

for i in range(0, total_passages, batch_size):
    batch_end = min(i + batch_size, total_passages)
    current_batch = all_passages[i:batch_end]
    
    chunks = []
    for passage in current_batch:
        url = passage.metadata.get('url', '')  # Get URL from metadata dictionary
        print(f"Processing URL: {url}")  # Debug print
        chunk = glm.Chunk(data={'string_value': passage.page_content})
        chunk.custom_metadata.append(glm.CustomMetadata(key="publish_date", numeric_value=19250101))
        if url:  # Only add URL metadata if we have a URL
            chunk.custom_metadata.append(glm.CustomMetadata(key="url", string_value=url))
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

