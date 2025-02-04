#Semantic Retrieval Gemini

service_account_file_name = 'service_account_key.json'

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(service_account_file_name)

scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])


import google.ai.generativelanguage as glm
generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)

from google.generativeai.types import HarmCategory, HarmBlockThreshold

from google.ai.generativelanguage import (
    GenerateAnswerRequest,
    HarmCategory,
    SafetySetting,
)

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
'''
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
'''

document_resource_name = "corpora/chroniclingamericatext-o3r7dekmxzmt/documents/01011925-cae4xw51jijj"

#%pip install -qU langchain-text-splitters
'''
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
first_10_items = passages[:10] 

chunks = []
for passage in first_10_items:
    #print(passage.page_content)
    chunk = glm.Chunk(data={'string_value': passage.page_content})
    chunk.custom_metadata.append(glm.CustomMetadata(key = "publish_date", numeric_value = 19250101))
    chunks.append(chunk)

# Make the request
print(len(chunks))
create_chunk_requests = []
for chunk in chunks:
    create_chunk_requests.append(glm.CreateChunkRequest(parent=document_resource_name, chunk=chunk))
request = glm.BatchCreateChunksRequest(parent=document_resource_name, requests=create_chunk_requests)
payload_size = len(create_chunk_requests)
print("Payload size:", payload_size, "bytes")
response = retriever_service_client.batch_create_chunks(request)
print(response)
'''

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

user_query = "What are the top two headlines for today, twenty words each?"
results_count = 5

# Add metadata filters for both chunk and document.
chunk_metadata_filter = glm.MetadataFilter(key='chunk.custom_metadata.publish_date',
                                           conditions=[glm.Condition(
                                              numeric_value = 19250101,
                                              operation=glm.Condition.Operator.EQUAL)])

# Make the request
# corpus_resource_name is a variable set in the "Create a corpus" section.
'''
request = glm.QueryCorpusRequest(name=corpus_resource_name,
                                 query=user_query,
                                 results_count=results_count,
                                 metadata_filters=[chunk_metadata_filter])
query_corpus_response = retriever_service_client.query_corpus(request)
print(query_corpus_response)
'''

answer_style = "ABSTRACTIVE" # Or VERBOSE, EXTRACTIVE
MODEL_NAME = "models/aqa"


safety_settings_set = [
     SafetySetting(
         category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
         threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
     ),
     SafetySetting(
         category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
         threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
     ),
     SafetySetting(
         category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
         threshold=HarmBlockThreshold.BLOCK_NONE,
     ),
     SafetySetting(
         category=HarmCategory.HARM_CATEGORY_HARASSMENT,
         threshold=HarmBlockThreshold.BLOCK_NONE,
     ),
 ]


# Make the request
# corpus_resource_name is a variable set in the "Create a corpus" section.
content = glm.Content(parts=[glm.Part(text=user_query)])
retriever_config = glm.SemanticRetrieverConfig(source=corpus_resource_name, query=content, metadata_filters=[chunk_metadata_filter])
req = glm.GenerateAnswerRequest(model=MODEL_NAME,
                                contents=[content],
                                semantic_retriever=retriever_config,
                                answer_style=answer_style,
                                safety_settings= safety_settings_set)
aqa_response = generative_service_client.generate_answer(req)
print(aqa_response)

'''
chunk_resource_name = aqa_response.answer.grounding_attributions[0].source_id.semantic_retriever_chunk.chunk
get_chunk_response = retriever_service_client.get_chunk(name=chunk_resource_name)
print(get_chunk_response)
'''