from flask import Flask,redirect,render_template,request,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import random
import os
import qrcode
from flask_mail import Mail,Message


app=Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_USERNAME']='ntharun832jacky@gmail.com'
app.config['MAIL_PASSWORD']='dogo ruiu ogty lrtp'
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

mail=Mail(app)




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db=SQLAlchemy(app)

class dogs_data(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30))
    about = db.Column(db.String(100), nullable=False)
    vaccination = db.Column(db.String(300),nullable=False)
    unique_id = db.Column(db.Integer) 


class bluecross_details(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    place = db.Column(db.String(30))
    email = db.Column(db.String(100), nullable=False)

class report_details(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    place= db.Column(db.String(30))
    email = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(300),nullable=False)
    unique_id = db.Column(db.Integer) 

@app.route("/", methods=['GET','POST'])
def home():
    return render_template('admin.html')


@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        name=request.form['Name']
        about=request.form['About']
        vaccination=request.form['Vaccination']
        unique_id=generate_unique_code()

        if unique_id:
            new_data = dogs_data(name=name,about=about,vaccination=vaccination,unique_id=unique_id)
            db.session.add(new_data)
            db.session.commit()
            generate_qr_code(unique_id)
            return render_template('create.html',success="Qr generated Successfully click hear to view Qr",unique_id=unique_id)

    return render_template('create.html')


@app.route('/update', methods=['GET','POST'])
def update():
    if request.method == 'POST':
        name=request.form['Name']
        about=request.form['About']
        vaccination=request.form['Vaccination']
        unique_id=request.form['Unique_id']
        
        unique_id_exist=dogs_data.query.filter_by(unique_id=unique_id).first()

        if unique_id_exist:
            unique_id_exist.name = name
            unique_id_exist.about += ' '+ about
            unique_id_exist.vaccination += ' '+ vaccination
            db.session.commit()
            return render_template('update.html',success="Value updated successfully")
        else:
            return render_template('update.html',error="Unique id not Matches")

    return render_template('update.html')

@app.route('/delete', methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        unique_id=request.form['Unique_id']
        if unique_id:
            filtered_data=dogs_data.query.filter_by(unique_id=unique_id).all()
            if filtered_data:
                for ids in filtered_data:
                    db.session.delete(ids)
                db.session.commit()
                return render_template("delete.html",success="Deleted Successfully")
            else:
                return render_template("delete.html",error="Incorrect Unique_id")
        else:
            return render_template("delete.html", error='Enter an unique id')
            
    return render_template("delete.html")

def generate_unique_code():
    return ''.join(str(random.randint(0,9)) for _ in range(6))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('created_picks', filename, as_attachment=True)




@app.route('/qr_redirect', methods=['GET', 'POST'])
def qr_redirect():
    unique_id = request.args.get('id')
    dog_val=dogs_data.query.filter_by(unique_id=unique_id).first()
    if dog_val:
        name=dog_val.name
        about=dog_val.about
        vaccination=dog_val.vaccination
        
        return render_template('home.html',unique_id=unique_id,name=name,about=about,vaccination=vaccination)
    else:
        return "not found"
    # return render_template('home.html',unique_id=unique_id)


def generate_qr_code(unique_identifier):
    # Construct URL with unique identifier
    url = f"http://192.168.1.4:5000/qr_redirect?id={unique_identifier}"
    
    # Generate QR code for the URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Define the folder path
    folder_path = "created_picks"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the image in the folder with the unique identifier as the filename
    img.save(os.path.join(folder_path, f"{unique_identifier}.png"))

@app.route("/delete_all")
def delete_all():
    details=db.session.query(dogs_data).all()
    for detail in details:
        db.session.delete(detail)
    db.session.commit()
    return render_template("admin.html")

@app.route("/admin_login")
def admin_login():
    datas=dogs_data.query.all()
    return render_template("admin_login.html",datas=datas)
    
@app.route("/report", methods=["GET", "POST"])
def report():
    unique_id=request.args.get("unique_id")
    places=bluecross_details.query.all()
    if request.method == "POST":
        place=request.form["place"]
        unique_id=request.form["Unique_id"]
        reason=request.form["reason"]
        email_blue=bluecross_details.query.filter_by(place=place).first()
        email=email_blue.email
        data=report_details(place=place, reason=reason, email=email,unique_id=unique_id)
        db.session.add(data)
        db.session.commit()
        send_mail(email,reason,unique_id)
        return render_template("report.html",success="email send successfully",places=places,unique_id=unique_id)
    
    return render_template("report.html",places=places,unique_id=unique_id)


def send_mail(email, reason, unique_id):
    if email:
        subject = f"Dog Details - {unique_id}"
        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
              <strong>Alert!</strong> Please pay attention to the following dog details:
            </div>
            <div style="border: 1px solid #ced4da; border-radius: 5px; padding: 15px; background-color: #fff;">
              <h1 style="color: #007bff;">Dog Details</h1>
              <p style="font-size: 18px;">Reason for inquiry: <strong>{reason}</strong></p>
              <p style="font-size: 18px;">Unique ID: <strong>{unique_id}</strong></p>
              <p style="font-size: 16px; color: #6c757d;">Thank you for your interest in our dogs!</p>
            </div>
          </body>
        </html>
        """
        sender = "ntharun832jacky@gmail.com"
        msg = Message(subject, sender=sender, recipients=[email])
        msg.html = body
        mail.send(msg)



if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True,host='0.0.0.0')




