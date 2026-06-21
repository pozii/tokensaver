"""Shared test fixtures."""
import pytest

SAMPLE_LONG_TEXT = """
Artificial intelligence has transformed the way we interact with technology.
Machine learning models can now understand natural language, generate images, and write code.
These advances have opened up new possibilities for automation and augmentation of human work.
However, with great power comes great responsibility.
AI systems can perpetuate biases present in training data.
They can also be used for harmful purposes if not properly governed.
The development of ethical AI frameworks is therefore critical.
Researchers and policymakers are working together to establish guidelines.
Companies are investing in safety teams dedicated to alignment research.
The goal is to ensure that AI benefits humanity as a whole.
Token efficiency is an important consideration for AI deployments at scale.
When API costs are high, every token matters significantly.
Developers need tools to compress context, cache results, and prune history.
This reduces both cost and latency for AI-powered applications.
The tokensaver MCP server addresses these needs directly.
It provides ten tools that together can reduce token usage by 60 to 97 percent.
""".strip()

SAMPLE_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant that answers questions clearly."},
    {"role": "user", "content": "Hello, can you help me?"},
    {"role": "assistant", "content": "Sure!"},
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris. It has been the country's capital since the 10th century and is home to famous landmarks like the Eiffel Tower, the Louvre, and Notre-Dame Cathedral."},
    {"role": "user", "content": "Got it."},
    {"role": "assistant", "content": "Is there anything else you would like to know?"},
    {"role": "user", "content": "Tell me about machine learning in detail."},
    {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It uses algorithms to find patterns in data and make predictions or decisions. There are three main types: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled training data. Unsupervised learning finds patterns without labels. Reinforcement learning trains agents through rewards and penalties. Deep learning, a subfield using neural networks, has driven many recent breakthroughs."},
]
