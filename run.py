from detector import create_interface

app = create_interface()

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, port=8000, host='localhost')