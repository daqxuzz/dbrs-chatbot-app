from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import openai
import os

# Initialize Flask app
app = Flask(__name__)
# Enable CORS (Cross-Origin Resource Sharing) to allow requests from your frontend.
CORS(app)

# --- Configure your AI (e.g., OpenAI) ---
# IMPORTANT: Set your OPENAI_API_KEY as an environment variable.
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("####################################################################")
    print("## WARNING: OPENAI_API_KEY environment variable not set.        ##")
    print("## The AI will use placeholder responses.                       ##")
    print("## Set the API key for full functionality.                      ##")
    print("####################################################################")

# --- Quotes Database ---
QUOTES_DB = {
    "general_uplift": [
        {"quote": "The best way out is always through.", "author": "Robert Frost"},
        {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
        {"quote": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
        {"quote": "You are braver than you believe, stronger than you seem, and smarter than you think.", "author": "A.A. Milne"},
        {"quote": "What lies behind us and what lies before us are tiny matters compared to what lies within us.", "author": "Ralph Waldo Emerson"}
    ],
    "sadness_comfort": [
        {"quote": "Tears are words that need to be written.", "author": "Paulo Coelho"},
        {"quote": "The word 'happy' would lose its meaning if it were not balanced by sadness.", "author": "Carl Jung"},
        {"quote": "It's okay to not be okay. It's okay to cry. Healing is a process, not a race.", "author": "Unknown"},
        {"quote": "Even the darkest night will end and the sun will rise.", "author": "Victor Hugo, Les Misérables"},
        {"quote": "Grief is the price we pay for love.", "author": "Queen Elizabeth II"}
    ],
    "anxiety_calm": [
        {"quote": "You don't have to control your thoughts. You just have to stop letting them control you.", "author": "Dan Millman"},
        {"quote": "The greatest weapon against stress is our ability to choose one thought over another.", "author": "William James"},
        {"quote": "Worrying does not take away tomorrow's troubles, it takes away today's peace.", "author": "Randy Armstrong"},
        {"quote": "Breathe. It's just a bad day, not a bad life.", "author": "Unknown"},
        {"quote": "Within you, there is a stillness and a sanctuary to which you can retreat at any time and be yourself.", "author": "Hermann Hesse"}
    ],
    "motivation_action": [
        {"quote": "Start by doing what's necessary; then do what's possible; and suddenly you are doing the impossible.", "author": "Francis of Assisi"},
        {"quote": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
        {"quote": "Our greatest glory is not in never falling, but in rising every time we fall.", "author": "Confucius"},
        {"quote": "The journey of a thousand miles begins with a single step.", "author": "Lao Tzu"}
    ],
    "self_reflection_awareness": [
        {"quote": "Knowing yourself is the beginning of all wisdom.", "author": "Aristotle"},
        {"quote": "The unexamined life is not worth living.", "author": "Socrates"},
        {"quote": "To find yourself, think for yourself.", "author": "Socrates"},
        {"quote": "The only journey is the one within.", "author": "Rainer Maria Rilke"}
    ],
    "opening_up_vulnerability": [
        {"quote": "Vulnerability sounds like truth and feels like courage. Truth and courage aren't always comfortable, but they're never weakness.", "author": "Brené Brown"},
        {"quote": "Sharing your story is an act of generosity and strength. It can heal you and help others.", "author": "Unknown"},
        {"quote": "The simple act of sharing can lighten a heavy heart and build bridges of understanding.", "author": "Unknown"}
    ],
    "seeking_tools_growth": [
        {"quote": "The first step towards getting somewhere is to decide you’re not going to stay where you are.", "author": "J.P. Morgan"},
        {"quote": "Small steps in the right direction can turn out to be the biggest step of your life.", "author": "Unknown"},
        {"quote": "Growth is never by mere chance; it is the result of forces working together.", "author": "James Cash Penney"}
    ]
}

def get_random_quote(category="general_uplift"):
    """Selects a random quote from the specified category, falling back to general_uplift."""
    if category not in QUOTES_DB or not QUOTES_DB[category]:
        category = "general_uplift" 
    
    quotes_list = QUOTES_DB[category]
    chosen_quote = random.choice(quotes_list)
    return f"\"{chosen_quote['quote']}\" - {chosen_quote['author']}"

# --- Real AI Integration ---
def get_ai_response(user_message, conversation_state, conversation_history=None):
    """
    Integrates with OpenAI GPT model for generating AI responses.
    `conversation_history` is a list of {"role": "user/assistant", "content": "message"} dicts.
    """
    if not openai.api_key:
        print("[AI Fallback] OpenAI API key not found. Using placeholder logic.")
        user_message_lower = user_message.lower()
        # Simplified placeholder responses
        if "hello" in user_message_lower or "hi" in user_message_lower:
            return "Hello there! It's good to hear from you. (AI offline - Please set API Key)"
        elif "sad" in user_message_lower:
            return "I'm sorry to hear you're feeling that way. Remember to be kind to yourself. (AI offline)"
        elif "anxious" in user_message_lower:
            return "It sounds like you're carrying a heavy load. Take a deep breath. (AI offline)"
        else:
            return "Tell me more about that. I'm here to listen. (AI offline)"

    # System prompt defines the AI's persona and instructions, now mentioning voice capability awareness.
    system_prompt = (
        "You are DBR's, a highly empathetic, insightful, and precise mental health companion. "
        "You are capable of understanding users whether they type or speak their messages. " # Added voice awareness
        "Your primary goal is to listen actively, understand deeply, and provide supportive, non-judgmental responses. "
        "When a user shares their feelings or problems, acknowledge them with genuine empathy and validate their experience. "
        "Offer constructive and thoughtful reflections. If appropriate, you can gently suggest coping strategies or perspectives, but always avoid giving prescriptive medical advice. "
        "Keep responses concise (around 1-3 sentences typically, unless more detail is clearly needed) yet meaningful. Encourage users to elaborate if they wish. "
        "Remember, you are a companion, not a therapist. If a user expresses severe distress, mentions self-harm, or is in crisis, "
        "your primary responsibility is to gently and clearly guide them to seek immediate professional help or contact a crisis hotline. "
        "For example, say: 'It sounds like you are going through a lot right now, and I want you to know you're not alone. For immediate support, please reach out to a crisis hotline or mental health professional. They are equipped to help you through this.' "
        "Always start your first response in a new conversation (after the initial greeting quote) with a warm, welcoming, and open-ended question related to their chosen startup option."
        "Maintain a calm, reassuring, and kind tone throughout the conversation."
    )
    
    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        messages.extend(conversation_history) 
    
    messages.append({"role": "user", "content": user_message})

    try:
        print(f"[AI Integration] Sending to OpenAI. Current user message: '{user_message}'. History length: {len(conversation_history) if conversation_history else 0}")
        
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages,
            temperature=0.75, 
            max_tokens=180,   
            top_p=1.0,
            frequency_penalty=0.1, 
            presence_penalty=0.1  
        )
        ai_reply = completion.choices[0].message.content.strip()
        print(f"[AI Integration] Received from OpenAI: {ai_reply}")
        return ai_reply
    except openai.APIError as e: 
        print(f"OpenAI API Error: {e}")
        return "I'm currently experiencing a slight hiccup connecting to my advanced understanding. Please try again in a moment. If the issue persists, we can try simpler topics."
    except Exception as e: 
        print(f"Error calling OpenAI API: {e}")
        return "I encountered an unexpected issue while processing your request. Let's try a different approach. How else can I help you today?"

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint to handle incoming messages and return bot responses.
    """
    try:
        data = request.get_json()
        user_message = data.get('message')
        current_state = data.get('conversationState', 'awaiting_startup_choice')
        conversation_history = data.get('history', []) 

        if not user_message:
            return jsonify({"reply": "I didn't receive a message.", "newState": current_state, "history": conversation_history}), 400

        bot_reply = ""
        new_state = current_state
        quote_for_greeting = None 

        print(f"[Backend] Received message: '{user_message}' in state: '{current_state}'. History length: {len(conversation_history)}")

        if current_state == 'awaiting_startup_choice':
            user_choice_lower = user_message.lower()
            base_reply_prompt = "" 
            quote_category = "general_uplift" 

            if "how are you feeling today?" in user_choice_lower:
                base_reply_prompt = "The user chose 'How are you feeling today?'. Ask them how they are feeling at this moment in a warm and open way."
                quote_category = "self_reflection_awareness"
                new_state = "chatting"
            elif "talk about what’s on your mind?" in user_choice_lower:
                base_reply_prompt = "The user chose 'Talk about what’s on your mind?'. Invite them to share what's on their mind, ensuring they feel it's a safe space."
                quote_category = "opening_up_vulnerability"
                new_state = "chatting"
            elif "relaxation techniques or motivational quotes?" in user_choice_lower:
                base_reply_prompt = "The user chose 'Relaxation techniques or motivational quotes?'. Ask them if they'd prefer a relaxation technique or a motivational quote first."
                quote_category = "seeking_tools_growth"
                new_state = "awaiting_technique_or_quote_choice" 
            elif "track your mood today?" in user_choice_lower: 
                base_reply_prompt = "The user chose 'Track your mood today?'. Acknowledge this choice, mention it's a demo for now, and gently transition to asking about their day or feelings."
                quote_category = "self_reflection_awareness"
                new_state = "chatting" 
            else: 
                base_reply_prompt = "The user has initiated a general chat. Greet them warmly and ask how you can help."
                new_state = "chatting"
            
            quote_for_greeting = get_random_quote(quote_category)
            initial_ai_response = get_ai_response(base_reply_prompt, new_state, []) 
            bot_reply = f"{quote_for_greeting}\n\n{initial_ai_response}"
            
            if initial_ai_response: # Add to history for client, though client manages its own primarily
                 pass # Client will add this to its log based on the response


        elif current_state == 'awaiting_technique_or_quote_choice':
            user_choice_lower = user_message.lower()
            if "breathing" in user_choice_lower or "exercise" in user_choice_lower or "technique" in user_choice_lower:
                bot_reply = "Okay, let's try a simple breathing exercise. Find a comfortable position. We'll do a 'box breath': Inhale for 4 counts, hold for 4, exhale for 4, and hold for 4. Are you ready to begin?"
                new_state = "doing_breathing_exercise_ready_prompt"
            elif "quote" in user_choice_lower:
                explicit_quote = get_random_quote("motivation_action") 
                bot_reply = f"Here's a quote for you: {explicit_quote}\n\nHow does that resonate with you, or what are you hoping to feel motivated about today?"
                new_state = "chatting" 
            else:
                clarification_prompt = f"The user was asked if they want a relaxation technique or a quote. Their response was '{user_message}'. Please gently ask them to clarify if they'd prefer a 'relaxation technique' or a 'motivational quote'."
                bot_reply = get_ai_response(clarification_prompt, new_state, conversation_history)
                new_state = "awaiting_technique_or_quote_choice" 
            

        elif current_state == 'doing_breathing_exercise_ready_prompt':
            user_choice_lower = user_message.lower()
            if "yes" in user_choice_lower or "ready" in user_choice_lower or "ok" in user_choice_lower:
                bot_reply = "Great. Let's start...\n\n(Imagine a calm voice guiding you)\n\n1.  **Inhale slowly** through your nose, counting to four: 1... 2... 3... 4.\n2.  **Hold your breath** gently for a count of four: 1... 2... 3... 4.\n3.  **Exhale slowly** through your mouth, counting to four: 1... 2... 3... 4.\n4.  **Hold your breath** again for a count of four: 1... 2... 3... 4.\n\nRepeat this cycle a few times. Take a moment. How do you feel after that?"
                new_state = "chatting" 
            elif "no" in user_choice_lower or "stop" in user_choice_lower:
                bot_reply = "That's perfectly okay. We can try another time, or perhaps something else. What's on your mind now?"
                new_state = "chatting"
            else:
                bot_reply = "I wasn't sure if that was a 'yes' for the breathing exercise. Let me know if you're ready, or if you'd prefer to do something else."
                new_state = "doing_breathing_exercise_ready_prompt" 
           

        elif current_state == 'chatting':
            bot_reply = get_ai_response(user_message, current_state, conversation_history)
            new_state = "chatting" 
            
        else:
            bot_reply = "It seems we're in an unexpected place in our conversation. Let's restart gently. How can I help you?"
            new_state = "awaiting_startup_choice" 
            # conversation_history = [] # Client will clear its history on reset

        print(f"[Backend] Sending reply: '{bot_reply}', New state: '{new_state}'")
        return jsonify({"reply": bot_reply, "newState": new_state})

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"reply": "I'm having a significant issue processing that right now. Please try again in a moment, or perhaps we can restart our conversation.", "newState": current_state}), 500

if __name__ == '__main__':
    print("Starting DBR's Companion backend server...")
    if not openai.api_key:
        print("Reminder: OpenAI API key not set. AI will use placeholder responses.")
    else:
        print("OpenAI API key found. AI should be functional.")
    app.run(host='0.0.0.0', port=5000, debug=True)
