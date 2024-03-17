from website import create_app

# Create the Flask app
app = create_app()

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5003)
