The following are my response to Set A questions:
Question 7: Yes, I would suggest using SFR-Embedding-Mistral for the model embedding. This is due to its speed and high performance metrics, which is far better than OpenAI's text-embedding-ada-002, according to MTEB text embeddings model leadership board.
Question 8: My alternative approach would be;
1. Embed the text chunks using SFR-Embedding-Mistral to boost speed and performance although at the cost of storage.
2. Save the embedded text as well as its context on pinecone vector database.
3. In the find-match function, I would get top-3 matches, then rerank them depending on which ones contain the tokens in the query.
4. Create a prompt using the context from step 3 above and the original user query.
5. Send the created prompt to generate answers for each question.
6. Return the best answer as response to the user.
