from flask import Flask, request, render_template_string
import boto3
import uuid
from datetime import datetime

app = Flask(__name__)

DYNAMODB_REGION = "eu-north-1"
SNS_REGION = "eu-north-1"
TOPIC_ARN = "arn:aws:sns:eu-north-1:155326049196:travelgo_notifications"

dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)
table = dynamodb.Table("travelgo_bookings")

sns = boto3.client("sns", region_name=SNS_REGION)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>TravelGo Backend</title>
    <style>
        body{
            font-family:Arial;
            background:#f4f6f9;
            padding:40px;
        }
        .card{
            max-width:500px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:10px;
            box-shadow:0 0 10px rgba(0,0,0,0.1);
        }
        input, select, button{
            width:100%;
            padding:10px;
            margin:10px 0;
        }
        button{
            background:#ff9900;
            color:white;
            border:none;
            cursor:pointer;
        }
    </style>
</head>
<body>
<div class="card">
    <h2>TravelGo Booking</h2>
    <form method="POST" action="/book">
        <input type="text" name="name" placeholder="Enter Name" required>
        <input type="email" name="email" placeholder="Enter Email" required>
        <input type="text" name="phone" placeholder="Enter Phone Number" required>

        <label>Destination</label>
        <select name="destination" required>
            <option value="">Select Destination</option>
            <option>Hyderabad</option>
            <option>Delhi</option>
            <option>Bangalore</option>
            <option>Mumbai</option>
        </select>

        <label>Travel Date</label>
        <input type="date" name="travel_date" required>

        <label>Transport</label>
        <select name="transport" required>
            <option value="">Select Transport</option>
            <option>Train</option>
            <option>Flight</option>
            <option>Bus</option>
        </select>

        <button type="submit">Book Now</button>
    </form>
</div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Booking Success</title>
    <style>
        body{
            font-family:Arial;
            background:#f4f6f9;
            padding:40px;
        }
        .card{
            max-width:500px;
            margin:auto;
            background:white;
            padding:30px;
            border-radius:10px;
            box-shadow:0 0 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
<div class="card">
    <h2>Booking Successful</h2>
    <p><strong>Booking ID:</strong> {{ booking_id }}</p>
    <p><strong>Name:</strong> {{ name }}</p>
    <p><strong>Email:</strong> {{ email }}</p>
    <p><strong>Phone:</strong> {{ phone }}</p>
    <p><strong>Destination:</strong> {{ destination }}</p>
    <p><strong>Travel Date:</strong> {{ travel_date }}</p>
    <p><strong>Transport:</strong> {{ transport }}</p>
    <p>Booking saved in DynamoDB and notification sent using SNS.</p>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/book", methods=["POST"])
def book():
    try:
        booking_id = str(uuid.uuid4())

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        destination = request.form["destination"]
        travel_date = request.form["travel_date"]
        transport = request.form["transport"]

        table.put_item(
            Item={
                "booking_id": booking_id,
                "name": name,
                "email": email,
                "phone": phone,
                "destination": destination,
                "travel_date": travel_date,
                "transport": transport,
                "created_at": datetime.utcnow().isoformat()
            }
        )

        message = f"""
TravelGo Booking Confirmed

Booking ID: {booking_id}
Name: {name}
Email: {email}
Phone: {phone}
Destination: {destination}
Travel Date: {travel_date}
Transport: {transport}
"""

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="TravelGo Booking Confirmation",
            Message=message
        )

        return render_template_string(
            SUCCESS_PAGE,
            booking_id=booking_id,
            name=name,
            email=email,
            phone=phone,
            destination=destination,
            travel_date=travel_date,
            transport=transport
        )

    except Exception as e:
        return f"Error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)