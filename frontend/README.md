# Praetorian DB-Forge Frontend

A simple web interface for interacting with the Praetorian DB-Forge API.

## Features

- Authenticate with an API key (saved in browser's local storage)
- View a list of active databases
- Spawn new databases
- Prune existing databases
- Create tables in databases
- Insert data into tables
- Query data from tables
- View service statistics
- Discover database instances

## Setup

1. Make sure the DB-Forge backend is running. If not, start it with:
   ```bash
   cd .. # Go to the root of the DB-Forge-MK1 project
   make up
   ```

2. Serve the frontend files. You can use any static file server. For example, with Python 3:
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```
   Or with Node.js (if you have `http-server` installed):
   ```bash
   cd frontend
   npx http-server -p 8000
   ```

3. Open your browser and navigate to `http://localhost:8000`.

## Usage

1. **Authentication**
   - Enter your API key in the "Authentication" section and click "Save API Key".
   - The API key will be saved in your browser's local storage and used for all subsequent requests.
   - You can clear the saved API key by clicking "Clear API Key".

2. **Database Management**
   - Use the "Spawn Database" section to create a new database.
   - Use the "Prune Database" section to remove an existing database.
   - Click "Refresh List" to see the current list of active databases.

3. **Service Statistics**
   - Click "Refresh Gateway Stats" to view statistics about the DB-Gateway service, including uptime, request counts, and error rates.

4. **Service Discovery**
   - Click "Discover Databases" to list all available database instances.

5. **Data Operations**
   - Use the "Create Table" section to define and create a new table in a database.
     - Columns should be specified as a JSON array. Example:
       ```json
       [
         {"name": "id", "type": "INTEGER", "primary_key": true},
         {"name": "name", "type": "TEXT", "not_null": true},
         {"name": "age", "type": "INTEGER"}
       ]
       ```
   - Use the "Insert Data" section to add rows to a table.
     - Data should be specified as a JSON array of objects. Example:
       ```json
       [
         {"name": "Alice", "age": 30},
         {"name": "Bob", "age": 25}
       ]
       ```
   - Use the "Query Data" section to retrieve data from a table.
     - You can specify simple key=value filters in the "Query Parameters" field, one per line.

## Notes

- The frontend communicates with the backend API at `http://localhost:8081` with the `Host` header set to `db.localhost`.
- Make sure this matches your Traefik configuration.
- For production use, you would want to serve this frontend through the same Traefik instance or a dedicated web server with proper SSL/TLS configuration.

## Development

The frontend is built with:
- HTML5
- CSS (Bootstrap 5)
- Vanilla JavaScript (ES6+)

Files:
- `index.html`: The main HTML structure
- `app.js`: The JavaScript logic
- Custom CSS is included in the `<style>` tag in `index.html`