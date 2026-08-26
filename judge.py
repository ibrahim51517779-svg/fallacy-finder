import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.6-flash")

def judge_arguments(topic, argument_a, argument_b):
    prompt = f"""You are an impartial debate judge.

Topic: {topic}

Argument A: {argument_a}

Argument B: {argument_b}

Evaluate both arguments on: logic, evidence, and persuasiveness.
Give each a score out of 10 for each criterion, a one-sentence reason,
and declare an overall winner. Be fair and don't favor either side by default."""

    response = model.generate_content(prompt)
    return response.text

# --- Run it ---
topic = input("Enter the debate topic: ")
argument_a = input("Enter Argument A: ")
argument_b = input("Enter Argument B: ")

result = judge_arguments(topic, argument_a, argument_b)
print("\n--- JUDGE'S VERDICT ---\n")
print(result)