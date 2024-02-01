# Import dependencies
from flask import Flask, request, jsonify
from config import OPENAI_API_KEY
import logging
from openai import OpenAI

# Initialize flask app
app = Flask(__name__)

# Create index route to accept post requests
@app.route('/', methods=['POST'])
def index(): 
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.json

        # Process the request
        response = process_request(body)
        
        return jsonify({'data': response})  
    else:
        return 'Content-Type not supported!' 
    

def process_request(body):
    # Get the client inputs
    input_1 = body.get('question_1')
    input_2 = body.get('question_2')
    input_3 = body.get('question_3')
    input_4 = body.get('question_4')

    # Set allowed fruits
    allowed_fruits = []

    # gpt prompt 
    prompt = ''

    # Task 1: 
    # Check client party on weekends
    if input_1.lower() == 'yes':
        # Add the weekend recommended fruits to allowed_fruits
        allowed_fruits.extend(['apples', 'pears', 'grapes', 'lemon', 'lime'])
        
        # Task 2
        # Check if they like cider
        if input_2.lower() == 'cider':
            # Clear the allowed list
            allowed_fruits.clear()

            # Add new recommendation to list
            allowed_fruits.extend(['apples', 'oranges', 'lemon', 'lime'])

        elif input_2.lower() == 'sweet':
            #Clear the allowed list
            allowed_fruits.clear()

            # Add new recommendation to list
            allowed_fruits.extend(['watermelon', 'oranges'])
        
        elif input_2.lower() == 'waterlike':
            #Clear the allowed list
            allowed_fruits.clear()

            # Add new recommendation to list
            allowed_fruits.extend(['watermelon'])
        
        elif input_2.lower() == 'grapes':           
            # Remove grape from recommendation list
            if 'watermelon' in allowed_fruits:   
                allowed_fruits.remove('watermelon')
       
       # Task 3
        if input_3.lower() == 'smooth':
            # Remove pears from list
            if 'pears' in allowed_fruits:
                allowed_fruits.remove('pears')

        elif input_3.lower() == 'slimy':
            # Create list without watermelon, lime and grapes
            recommended = [x for x in allowed_fruits if x not in ['watermelon', 'lime', 'grape']]

            # Clear allowed fruits
            allowed_fruits.clear()

            # Copy recommended to allowed fruits
            allowed_fruits = recommended.copy()
        elif input_3.lower() == 'waterlike':
            # Remove watermelon
            if 'watermelon' in allowed_fruits:   
                allowed_fruits.remove('watermelon')

        # Task 4        
        if int(input_4[-1]) < 3:
            # Remove lime
            if 'lime' in allowed_fruits:    
                allowed_fruits.remove('lime')
            
            # Remove watermelon
            if 'watermelon' in allowed_fruits:    
                allowed_fruits.remove('watermelon')

        elif int(input_4[-1]) > 4 and int(input_4[-1]) < 7:
            # Remove pears
            if 'pears' in allowed_fruits:
                allowed_fruits.remove('pears')

            # Remove apples
            if 'apples' in allowed_fruits:
                allowed_fruits.remove('apples')
   
    # Create prompt
    if len(allowed_fruits) > 1:
        prompt = f"Please recommend some fruits from the following; {', '.join(allowed_fruits)} for me for a weekend party."       
    else:
        prompt = f"Say based on your budget, you can take {''.join(allowed_fruits)}!"
    
    # Send prompt to gpt for response
    response = get_gpt_response(prompt)

    return response

def get_gpt_response(prompt):    
    try:
        # Initialize client
        client = OpenAI(api_key=OPENAI_API_KEY) 
        
        # Make request
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": prompt}]
        )

        # Return response
        return response.choices[0].message.content
    except Exception as err:
        logging.error(f"Unable to get response from gpt due to error: {err}")
        return None

# Configure the server
if __name__ == '__main__':
    app.run(debug=True)

