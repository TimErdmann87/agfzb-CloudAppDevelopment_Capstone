const express = require('express');
const app = express();
const port = process.env.PORT || 3000;
const Cloudant = require('@cloudant/cloudant');

// Initialize Cloudant connection with IAM authentication
async function dbCloudantConnect() {
    try {
        const cloudant = Cloudant({
            plugins: { iamauth: { iamApiKey: 'iqUvipPVcLRc19MF7reTg45AfQijLCtAlsXjq5eLAW7U' } },
            url: 'https://81468b94-91ea-46c8-81cd-d7bf3bc9be3a-bluemix.cloudantnosqldb.appdomain.cloud',
        });

        const db = cloudant.use('dealerships');
        console.info('Connect success! Connected to DB');
        return db;
    } catch (err) {
        console.error('Connect failure: ' + err.message + ' for Cloudant DB');
        throw err;
    }
}

let db;

(async () => {
    db = await dbCloudantConnect();
})();

app.use(express.json());

// Define a route to get all dealerships with optional state and ID filters
app.get('/api/dealership', (req, res) => {
    const { state, id } = req.query;

    // Create a selector object based on query parameters
    const selector = {};
    if (state) {
        selector.state = state;
    }
    
    if (id) {
        selector.id = parseInt(id); // Filter by "id" with a value of 1
    }

    const queryOptions = {
        selector,
        limit: 10, // Limit the number of documents returned to 10
    };

    db.find(queryOptions, (err, body) => {
        if (err) {
            console.error('Error fetching dealerships:', err);
            res.status(500).json('Something went wrong on the server');
        } else {
            const dealerships = body.docs;
            
            if (dealerships.length === 0) {
                if (state && id) {res.status(404).json("This combination of 'state' and 'id' does not exist");}
                else if (state) {res.status(404).json('The state does not exist');}
                else if (id) {res.status(404).json('The id does not exist');}
            }
            else {
                res.json(dealerships);
            }
        }
    });
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});