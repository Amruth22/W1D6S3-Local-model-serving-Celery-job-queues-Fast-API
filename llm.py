from llama_cpp import Llama
from config.settings import MAX_NEW_TOKENS, TEMPERATURE, TOP_P

# Global variable for the model
model = None

def load_model():
    """Load the GGUF LLM model"""
    global model
    
    if model is None:
        print("Loading Llama 3.2 1B GGUF model...")
        model = Llama.from_pretrained(
            repo_id="bartowski/Llama-3.2-1B-Instruct-GGUF",
            filename="Llama-3.2-1B-Instruct-Q4_K_M.gguf",
            n_ctx=2048,  # Set context window to 2048 tokens
            verbose=False  # Reduce verbose output
        )
        print("GGUF model loaded successfully!")
    return model

def generate_response(prompt):
    """Generate a response for a given prompt using GGUF model"""
    global model
    
    # Load model if not already loaded
    if model is None:
        model = load_model()
    
    # Handle RAG prompts with context
    if "Context:" in prompt and "Question:" in prompt:
        # Extract context and question from the prompt
        context_start = prompt.find("Context:") + len("Context:")
        context_end = prompt.find("Question:")
        context = prompt[context_start:context_end].strip()
        
        question_start = prompt.find("Question:") + len("Question:")
        question_end = prompt.find("Answer:")
        if question_end == -1:  # If "Answer:" is not found
            question = prompt[question_start:].strip()
        else:
            question = prompt[question_start:question_end].strip()
        
        # Format as a proper instruction with context
        full_prompt = f"Use the following context to answer the question:\n\nContext: {context}\n\nQuestion: {question}"
    else:
        # Handle simple question prompts
        if "Question:" in prompt and "Answer:" in prompt:
            question_start = prompt.find("Question:") + len("Question:")
            question_end = prompt.find("Answer:")
            full_prompt = prompt[question_start:question_end].strip()
        else:
            full_prompt = prompt
    
    # Generate response using chat completion
    response = model.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        max_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P
    )
    
    # Extract and return the answer
    # Handle different response formats
    if isinstance(response, dict) and 'choices' in response:
        result = response['choices'][0]['message']['content']
    elif isinstance(response, dict) and 'content' in response:
        result = response['content']
    else:
        result = str(response)
        
    return result.strip()

def main():
    """Main QA interface"""
    # Load model
    load_model()
    
    # Question-answering loop
    print("\nLlama 3.2 1B GGUF Question-Answering Interface")
    while True:
        user_input = input("\nQuestion: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
            
        # Format prompt for question answering
        prompt = f"Question: {user_input}\nAnswer:"
        
        # Generate response
        answer = generate_response(prompt)
        print(f"Answer: {answer}")

if __name__ == "__main__":
    main()