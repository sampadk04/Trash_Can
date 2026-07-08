Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.

---

# Top-k Performance Evaluation

I want to update our V2 architecture to potentially make the latency lower.

Inorder to do that we want to potentially parallelize the LLM calls for the PreProcessor and MID blocks.

Now, currently we are inherently forced to make sequential calls for the PreProcessor and MID blocks because we sort of use the re-phrased query from the PreProcessor block to use it to identify the top-k intents to send to the MID block.
If we can somehow only use the current turn's raw query (and maybe previous turn's re-phrased query) to reliably identify the top-k intents to send to the MID block, then we can parallelize the PreProcessor and MID blocks. (We won't have to rely on just the current turn's re-phrased query to identify the top-k intents to send to the MID block.)

So, inorder to reliably decide if we can parallelize the PreProcessor and MID blocks we need to evaluate the performance of the following scenarios ->
Case 1: Suppose we are at Turn 'i'. In this turn we are using the raw user query directly for top-k.
Case 2: Suppose we are at Turn 'i'. In this turn we are using re-phrased query from Pre-processor.
Case 3: Suppose we are at Turn 'i'. In this turn we are using the re-phrased query from Pre-processor and the raw query from Turn 'i-1' appended with the current turn's raw query as string for top-k.
Case 4: Suppose we are at Turn 'i'. In this turn we will use the re-phrased query from Pre-processor from Turn 'i-1' and get the top-k. We will also use the raw query from Turn 'i' and get the top-k. Then we will then take the union (and combine based on the rankings) of the top-k intents from both and send it to the MID block.



Inorder to evaluate these cases properly and easier we will need to setup the following ->
- A dataset of user queries and their corresponding expected intents. (Note: We only care about the top-k intents for each query, and what is their ranking, we want the expencted intent to be ranked as high as possible)
- We should have 2 different types of datasets ->
    * One where the query should be explicit in terms of the intent they want. Here the passing criterion is simple, the expected intent (or target intent) should be in the top-k intents returned by the model.
    * The other where, the query is ambigous, but upon clearing ambiguity, the expected intent should be in the top-k intents returned by the model.
    Here the passing criterion is more fluid. 
    If we are in the MID Is Ambiguos State (and the user is repsonding, this response should be part of the dataset), then the expected intent should be in the top-k intents
    * The second query is ambigous dataset is something we will create later, for now we will focus on the first dataset, where the query is explicit in terms of the intent they want and the top-k should directly contain the expected intent.
    * Store the dataset inside the 'data' folder.
- We will also need a wrapper functions to wrap the embedding model and the top-k retrival code from redis (this should automatically adapt according the V2 code).
- We should be able to easily switch the strategy for each run.
- The run should decide what all columns to have in the final csv.
