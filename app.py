from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://lambdaReadWriteUser:aymankh123@cluster0.couco.mongodb.net/?retryWrites=true&w=majority")
db = cluster["bakery"]
users = db['users']
orders = db['orders']

app = Flask(__name__)

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From").replace("whatsapp:", "")
    response = MessagingResponse()
    user = users.find_one({"number": number})
    if not user:
        response.message("Hi, thanks for contacting *The Red velvet*.\nYou can choose from one of the options below: "
                         "\n\n*Type*\n\n 1. To *contact* us \n 2. To *order* snacks \n 3. To know our *working hours*\n"
                         "4. To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user['status'] == 'main':
        try:
            option = int(text)
            if option == 1:
                response.message("You can contact us through phone or e-mail.\n\n*Phone*: 999887 \n*E-mail:* contact@email.com")
            elif option == 2:
                response.message("You have entered *ordering mode*.")
                users.update_one({"number": number}, {"$set": {"status": "ordering"}})
                response.message("You can select one of the following cakes to order:\n\n1. cake1\n2. cake2\n3. cake3\n0. Go back")
            elif option == 3:
                response.message("We work everyday from *9 AM to 9 PM*")
            elif option == 4:
                response.message("We have many centers across the city. Our main: Istanbul/Turkey")
            
        except:
            response.message("Please enter a valid response")
            return str(response)
    elif user['status'] == 'ordering':
        try:
            option = int(text)
        except:
            response.message("Please enter a valid response")
            return str(response)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            response.message("You can choose from one of the options below: "
                         "\n\n*Type*\n\n 1. To *contact* us \n 2. To *order* snacks \n 3. To know our *working hours*\n"
                         "4. To get our *address*")
        elif 1 <= option <= 3:
            cakes = ["cake 1", "cake 2", "cake 3"]
            selected = cakes[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            response.message("Excellenet choice 😉")
            response.message("Please enter your address to confirm the order")
        else:
            response.message("Please enter a valid response")
    if user['status'] == 'address':
        selected = user['item']
        response.message("Thanks for shopping with us!")
        response.message(f"Your order for {selected} has been received and will be delivered within an hour")
        orders.insert_one({"number": number, "item": selected, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user['status'] == 'ordered':
        response.message("Hi, thanks for contacting again *The Red velvet*.\nYou can choose from one of the options below: "
                         "\n\n*Type*\n\n 1. To *contact* us \n 2. To *order* snacks \n 3. To know our *working hours*\n"
                         "4. To get our *address*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    else:
        response.message("I don't know what to say")

    users.update_one({'number': number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(response)


if __name__ == '__main__':
    app.run()
