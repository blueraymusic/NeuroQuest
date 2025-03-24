import google.generativeai as genai


API_KEY = "AIzaSyDY6ylgqJc0YZUVe7YEamBK29IKA7_wl_Q"
genai.configure(api_key=API_KEY)


model = genai.GenerativeModel('gemini-1.5-flash')

def chat_with_gemini(prompt):
    response = model.generate_content([prompt])  
    return response.text if response.text else "No response"


if __name__ == "__main__":
    print("Gemini Chatbot (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat...")
            break
        response = chat_with_gemini(user_input)
        print("Gemini:", response)
