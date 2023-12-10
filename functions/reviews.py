from cloudant.client import Cloudant
from cloudant.query import Query
from flask import Flask, jsonify, request, abort
import atexit

#Add your Cloudant service credentials here
cloudant_username = '81468b94-91ea-46c8-81cd-d7bf3bc9be3a-bluemix'
cloudant_api_key = 'iqUvipPVcLRc19MF7reTg45AfQijLCtAlsXjq5eLAW7U'
cloudant_url = 'https://81468b94-91ea-46c8-81cd-d7bf3bc9be3a-bluemix.cloudantnosqldb.appdomain.cloud'
client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)

session = client.session()
print('Databases:', client.all_dbs())

db = client['reviews']

app = Flask(__name__)

@app.route('/api/review', methods=['GET'])
def get_reviews():
    dealership_id = request.args.get('dealerId')

    # Check if "id" parameter is missing
    if dealership_id is None:
        return jsonify({"error": "Missing 'dealerId' parameter in the URL"}), 400

    # Convert the "id" parameter to an integer (assuming "id" should be an integer)
    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'delaerId' parameter must be an integer"}), 400

    # Define the query based on the 'dealership' ID
    selector = {
        'dealership': dealership_id
    }

    # Execute the query using the query method
    try:
        result = db.get_query_result(selector)
    except CloudantException as cloudant_exception:
        print("Error: ", cloudant_exception)
        return jsonify({"error": "Something went wrong on the server"}), 500
    except (requests.exceptions.RequestException, ConnectionResetError) as err:
        print("Error - Connection: ", err)
        return jsonify({"error": "Something went wrong on the server"}), 500

    # Create a list to store the documents
    data_list = []

    # Iterate through the results and add documents to the list
    for doc in result:
        data_list.append(doc)

    if len(data_list) == 0:
        return jsonify({"error": "Provided 'dealerId' does not exist"}), 404

    # Return the data as JSON
    return jsonify(data_list)


@app.route('/api/review', methods=['POST'])
def post_review():
    if not request.json:
        abort(400, description='Invalid JSON data')
    
    # Extract review data from the request JSON
    review_data = request.json["review"]

    # Validate that the required fields are present in the review data
    required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
    for field in required_fields:
        if field not in review_data:
            abort(400, description=f'Missing required field: {field}')

    # Save the review data as a new document in the Cloudant database
    db.create_document(review_data)

    return jsonify({"message": "Review posted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)