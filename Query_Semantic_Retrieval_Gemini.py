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
    HarmCategory,
    SafetySetting,
)

corpus_resource_name = "corpora/chroniclingamericatext-o3r7dekmxzmt"

user_query = "I am a female in 2025, how am I feeling and why? The response should be 50 words long."
results_count = 5

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

# Add metadata filters for both chunk and document.
chunk_metadata_filter = glm.MetadataFilter(key='chunk.custom_metadata.publish_date',
                                           conditions=[glm.Condition(
                                              numeric_value = 19250101,
                                              operation=glm.Condition.Operator.EQUAL)])

# Make the request
# corpus_resource_name is a variable set in the "Create a corpus" section.
content = glm.Content(parts=[glm.Part(text=user_query)])
retriever_config = glm.SemanticRetrieverConfig(source=corpus_resource_name, query=content, metadata_filters=[chunk_metadata_filter])
req = glm.GenerateAnswerRequest(model=MODEL_NAME,
                                contents=[content],
                                temperature = 0.1,
                                semantic_retriever=retriever_config,
                                answer_style=answer_style,
                                safety_settings= safety_settings_set)
aqa_response = generative_service_client.generate_answer(req)
print(user_query)
print(aqa_response.answer.content.parts[0].text)
#print(aqa_response)

#chunk_resource_name = aqa_response.answer.grounding_attributions[0].source_id.semantic_retriever_chunk.chunk
#get_chunk_response = retriever_service_client.get_chunk(name=chunk_resource_name)
#print(get_chunk_response)

