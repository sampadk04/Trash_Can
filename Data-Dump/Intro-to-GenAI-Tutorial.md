# Resources Link

## Visualizations:
- https://poloclub.github.io/transformer-explainer/
- Paper: "Transformer Explainer: Learning LLM Transformers with Interactive Visual Explanation and Experimentation" - https://dl.acm.org/doi/pdf/10.1145/3772318.3791725
- "LLM Visualization"- https://bbycroft.net/llm
- "Word 2 Vec Visualizer" - https://projector.tensorflow.org/
-  

## Articles:
- "Generative AI exists because of the transformer. This is how it works" - https://ig.ft.com/generative-ai/
- 

## Games:
- https://research.google.com/semantris/



## CMI Intro to GenAI Elective:
The “Intro to Gen AI” course contains six lecture decks and 198 slides. It is primarily an LLM course, expanding into multimodal generation, diffusion models, RAG, industry applications, and AI risks.

## Topics by lecture

1. LLM foundations and Transformer internals :codex-file-citation{path="/Users/sampadk04/Desktop/Coding/Non_GitHub/Interview-Prep/Resources/CMI-Courses/Intro-to-GenAI/01-LLM-01.pdf" purpose="source"}

- What large language models are
- Autoregressive next-token prediction
- GPT and the Transformer decoder
- Tokenization: words, subwords, BPE, SentencePiece, and tiktoken
- Token embeddings and positional encoding
- Transformer/GPT blocks
- Self-attention: queries, keys, values, and attention scores
- Causal attention masking and multi-head attention
- Feed-forward networks, residual connections, dropout, and LayerNorm
- Output distributions and token sampling
- Cross-entropy training and perplexity

2. Evolution of NLP, BERT, GPT, prompting, and RLHF :codex-file-citation{path="/Users/sampadk04/Desktop/Coding/Non_GitHub/Interview-Prep/Resources/CMI-Courses/Intro-to-GenAI/02-LLM-02.pdf" purpose="source"}

- NLP evolution: LSA, Word2Vec, GloVe, ELMo, BERT, and GPT
- Context-free versus contextual embeddings
- Limitations of RNNs and LSTMs
- Transformer encoder-decoder architecture
- BERT pretraining:
  - Masked language modelling
  - Next-sentence prediction
  - Fine-tuning and downstream NLP tasks
  - BERT variants
- GPT-1 through GPT-4 and multimodal GPT
- Zero-shot and few-shot learning
- Prompt engineering and chain-of-thought prompting
- Generation controls: temperature, top-k, and top-p
- Function calling and LLM application frameworks
- Instruction fine-tuning
- RLHF:
  - Human preference data
  - Reward/preference models
  - Proximal Policy Optimization
  - Reward hacking, hallucination, and alignment limitations

3. Scaling laws, efficient fine-tuning, and model efficiency :codex-file-citation{path="/Users/sampadk04/Desktop/Coding/Non_GitHub/Interview-Prep/Resources/CMI-Courses/Intro-to-GenAI/03-LLM-03.pdf" purpose="source"}

- LLM scaling laws involving model size, dataset size, and compute
- Power-law relationships between scale and loss
- Compute-optimal training and the Chinchilla findings
- Data scarcity and repeated-data effects
- Data augmentation, deduplication, and data quality
- Pretraining followed by task-specific fine-tuning
- Foundation models and LLaMA
- Parameter-efficient fine-tuning
- LoRA and low-rank weight updates
- Model quantization and QLoRA
- Sparse attention: BigBird and Longformer
- FlashAttention and GPU memory movement
- Mixture-of-Experts architectures

4. Multimodal models, VAEs, and GANs :codex-file-citation{path="/Users/sampadk04/Desktop/Coding/Non_GitHub/Interview-Prep/Resources/CMI-Courses/Intro-to-GenAI/04-LLM-04.pdf" purpose="source"}

- Multimodal deep learning
- Image captioning with CNN-RNN systems
- CLIP:
  - Contrastive language-image pretraining
  - Joint text-image embedding spaces
  - Zero-shot image classification
  - Multimodal search
  - Prompt engineering and robustness
- Vision Transformers:
  - Image patch embeddings
  - Positional embeddings
  - Attention complexity
  - Inductive bias and data-scaling requirements
- Other multimodal models:
  - Whisper
  - PaLM-E
  - CoCa, Flamingo, and Kosmos-1
  - Video-language models
- Variational Autoencoders:
  - Autoencoder bottlenecks
  - Regularized latent spaces
  - Image generation and limitations
- Generative Adversarial Networks:
  - Generator-discriminator training
  - Minimax objective
  - Mode collapse and training instability

5. Diffusion models for image generation :codex-file-citation{path="/Users/sampadk04/Desktop/Coding/Non_GitHub/Interview-Prep/Resources/CMI-Courses/Intro-to-GenAI/05-Diffusion Models.pdf" purpose="source"}

- Forward diffusion through Gaussian noise
- Reverse diffusion and denoising
- Denoising Diffusion Probabilistic Models
- Likelihood-based training and variational objectives
- Reparameterization of the diffusion process
- Predicting noise instead of directly predicting images
- Mean-squared-error training objective
- U-Net denoising architecture
- Conditional and classifier-guided diffusion
- CLIP-guided generation
- Latent-space versus pixel-space diffusion

6. RAG, industry applications, research directions, and risks :codex-file-citation{path="/Users/sampadk04/Desktop/Coding/Non_GitHub/Interview-Prep/Resources/CMI-Courses/Intro-to-GenAI/06-LLM-06.pdf" purpose="source"}

- Retrieval-Augmented Generation:
  - Motivation and grounding
  - RAG versus fine-tuning
  - Document chunking and overlap
  - Embeddings and similarity search
  - Vector databases
  - Flat, inverted-file, HNSW, dense, sparse, and hybrid retrieval
  - Re-ranking retrieved chunks
  - Knowledge-graph RAG
  - Joint retriever-generator optimization
- Enterprise GenAI:
  - Productivity copilots
  - RAG applications
  - Specialized AI agents
  - Legal, software, sales, education, and design use cases
- Transformers beyond language:
  - Protein sequences
  - Time-series forecasting
  - Geometry
  - Music and dance generation
- Research directions:
  - Robustness and adversarial resistance
  - Efficient training and inference
  - Specialized scientific applications
  - Interpretability, fairness, transparency, and privacy
- Societal risks:
  - Misinformation and deepfakes
  - Intellectual property
  - Bias
  - Adversarial attacks
  - Concentration and monopolization of AI power
  - Sentience, machine intelligence, and existential-risk questions

The folder also references the [official CMI course page](https://www.cmi.ac.in/~pranabendu/genai24/).
