from flask import Flask,request,render_template,url_for,redirect,session,flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash,check_password_hash
import re

app=Flask(__name__)
app.secret_key="miniproject"

mongo_url="mongodb+srv://rameshprathapsakthikalai:OwMYWHeUq9cgXvHK@cluster0.thdk3.mongodb.net/"
client=MongoClient(mongo_url)
db=client.student
collection=db.ministd
std_job=db.stdjob
collection_signup=db.miniuserpassword

def pwd(password):
    if (len(password)<=8):
        return False
    elif not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password) or not re.search(r"\d",password):
        return False
    elif not re.search(r"[@#_$%^&*<>]",password):
        return False
    else:
        return True

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")
        if collection_signup.find_one({"username":name}):
             flash("username already exist", 'danger')
             return redirect(url_for('signup'))
        else:
            if not pwd(password):
                flash('Password should be at least 8 characters long and contain uppercase, lowercase, digit, and special characters.', 'danger')
                return redirect(url_for('signup'))                
            else:
                hashpwd=generate_password_hash(password)
                userpwd_dic={}       
                userpwd_dic.update({"username":name})
                userpwd_dic.update({"password":hashpwd})
                collection_signup.insert_one(userpwd_dic)
                session["sessionname"]=name
                return redirect(url_for('insert'))            
    return render_template("signup.html")

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        name=request.form.get("username")
        password=request.form.get("password")   
        login_data=collection_signup.find_one({"username":name})
        if login_data and check_password_hash(login_data["password"],password):
            session["sessionname"]=name
            return redirect(url_for('home'))
        else:
            return "check username and password...."
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("session",None)
    return redirect(url_for('login'))


@app.route("/insert",methods=["GET","POST"])
def insert():
    if request.method=="POST":
        name=session["sessionname"]
        rollno=request.form.get("rollno")
        age=request.form.get("age")       
        mobileno=request.form.get("mobileno")
        address=request.form.get("address")
        emp_dic={}
        emp_dic.update({"Name":name})
        emp_dic.update({"Roll_no":rollno})
        emp_dic.update({"Age":age})        
        emp_dic.update({"Mobile_no":mobileno})
        emp_dic.update({"Address":address})        
        collection.insert_one(emp_dic)
        return redirect(url_for('home'))   
    return render_template("insert.html")

@app.route("/home")
def home():    
    if session["sessionname"]:
        data=collection.find_one({"Name":session["sessionname"]})
    return render_template("home.html",name=data)

@app.route("/table",methods=["GET","POST"])
def table():
    if request.method=="POST":
        date=request.form.get("date")
        data1=std_job.find_one({"Date":date})            
        if not data1:
            return render_template("table.html")
        elif data1:    
            onedate=data1["Date"]            
            if onedate==date:
                data=std_job.find({"Date":date,"Name":session["sessionname"]})
                return render_template("table.html",data=data)
        else:
            return render_template("table.html")
    return render_template("table.html")
    

@app.route("/addmark",methods=["GET","POST"])
def addwork():
    if request.method=="POST":
        name=request.form.get("name")
        date=request.form.get("date")
        starttime=request.form.get("starttime")
        endtime=request.form.get("endtime")
        job=request.form.get("job")
        std_work={}
        std_work.update({"Name":name})
        std_work.update({"Date":date})
        std_work.update({"Start_time":starttime})
        std_work.update({"End_time":endtime})
        std_work.update({"Job":job})        
        std_job.insert_one(std_work)     
        return redirect(url_for('table'))
    return render_template("workform.html")

@app.route("/edit/<string:id>",methods=["GET","POST"])
def edit(id):
    if request.method=="POST":
        name=request.form.get("name")
        date=request.form.get("date")
        starttime=request.form.get("starttime")
        endtime=request.form.get("endtime")
        job=request.form.get("job")    
        std_job.update_one({"_id":ObjectId(id)},
                              {"$set":{"Name":name,"Date":date,"Start_time":starttime,"End_time":endtime,"Job":job,}})
        return redirect(url_for('table'))    
    data=std_job.find_one({"_id":ObjectId(id)})
    return render_template("workformedit.html",data=data)

@app.route("/delete/<string:id>")
def delete(id):
    std_job.delete_one({"_id":ObjectId(id)})
    return redirect(url_for('table'))    

if __name__=="__main__":
    app.run(debug=True)