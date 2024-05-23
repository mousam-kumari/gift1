from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import re

app = Flask(__name__)
# Your Gemini API key
GEMINI_API_KEY = 'AIzaSyCclRMJ0cdftV0xAhHS7yPEyMWbc3TZtPs'

products_schema = [
    {
        "Product_name": "Eco-friendly Water Bottle",
        "Reason": "Chosen for its environmental benefits and the growing consumer preference for sustainable products."
    },
]

# Initialize the Gemini API client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_gift_idea', methods=['POST'])
def generate_gift_idea():
    data = request.json
    age = data.get('age')
    gender = data.get('gender')
    occasion = data.get('occasion')
    recipient_type = data.get('recipient_type')
    categories = data.get('categories')
    price_range = data.get('price_range')

    # Convert categories list to a string for the prompt
    categories_str = ', '.join(categories)

    prompt = (f"You have a very good choice, so just provide me a list of 9 highly-rated and trending different gift ideas with a specific product that can be searched using the product name, for Indian people "
              f"for a {age}-year-old {recipient_type} who is {gender} and loves {categories_str} items. These gifts should be suitable for {occasion}, "
              f"available on Amazon India, and within the price range {price_range}. Ensure that each product is followed by its product_name, "
              f"and each product is followed by a convincing reason for its selection for Indian people in brief. Ensure that the products are listed without any "
              f"special characters such as *, -, here is an example:\n"
              f"Product_name: Eco-friendly Water Bottle\n"
              f"Reason: Chosen for its environmental benefits and the growing consumer preference for sustainable products.\n"
              f"Generate 9 products with product_name and reason for selection as a gift idea. Each reason should be just below the product name.")

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
     # Print the raw response
        cleaned_text = clean_text(raw_text)
        gift_ideas = process_and_structure_gift_ideas(cleaned_text)
      # Debug logging
        return jsonify({"gift_ideas": gift_ideas})
    except Exception as e:
        print(f"Error generating gift ideas: {e}")
        return jsonify({"error": "Error generating gift ideas"}), 500

@app.route('/search_gift_idea', methods=['POST'])
def search_gift_idea():
    data = request.json
    textdata = data.get('prompt')
    prompt = (f"Task: Gift idea generation\nDescription: Based on {textdata} generate gift idea suggestions that are available on Amazon India ecommerce website. "
              f"Ensure that only the product names and reasons are provided as examples in the schema {products_schema}. Additionally, include each product "
              f"followed by its reason for selection. Provide me the output in the format:\nProduct_name:\nReason:")

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
         # Print the raw response
        cleaned_text = clean_text(raw_text)
        gift_ideas = process_and_structure_gift_ideas(cleaned_text)
      # Debug logging
        return jsonify({"gift_ideas": gift_ideas})
    except Exception as e:
        print(f"Error generating gift ideas: {e}")
        return jsonify({"error": "Error generating gift ideas"}), 500

def clean_text(text):
    return re.sub(r'[*-]', '', text)

def process_and_structure_gift_ideas(text):
    lines = text.split('\n')
    gift_ideas = []
    current_gift = {}

    for line in lines:
        if "Product_name:" in line:
            if current_gift:
                gift_ideas.append(current_gift)
                current_gift = {}
            current_gift["Product_name"] = line.replace("Product_name:", "").strip()
        elif "Reason:" in line:
            current_gift["Reason"] = line.replace("Reason:", "").strip()

    if current_gift:
        gift_ideas.append(current_gift)

    # Ensure we have exactly 9 gift ideas, pad with empty entries if necessary
    while len(gift_ideas) < 9:
        gift_ideas.append({"Product_name": "N/A", "Reason": "N/A"})

    return gift_ideas[:9]

if __name__ == '__main__':
    app.run(debug=True)
