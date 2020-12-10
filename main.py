from builtins import str
from flask import Flask,render_template,request,redirect,url_for,flash,session
from forms import RegistrationForm,LoginForm,DepartmentForm,EmptyForm,AddProject
from flask_wtf.file import FileField,FileAllowed
import psycopg2 as psql
from passlib.hash import pbkdf2_sha256
import random
import shutil
import datetime
import os
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f5f907b5a9c962dd62e896f08c13a609'
PEOPLE_FOLDER=os.path.join('static','media/profile_image')
app.config['UPLOAD_FOLDER']=PEOPLE_FOLDER
 
conn=psql.connect("dbname='p1' user='postgres' host='localhost' password='1234'")
#-----------------------------------------------------------------------------------------------------------
def dataret(email):
    cursor=conn.cursor()
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='register'")
    list1 = [a[0] for a in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM register where email='{email}'")
    dict1 = dict(zip(tuple(list1), cursor.fetchone()))
    return dict1

#======================================homepage================================================================
@app.route('/')
def home():
    if(session.get('logged-in')):
        if(session['username'][0]=='A'):
            return redirect(url_for('ahome'))
        if(session['username'][0]=='E'):
            return redirect(url_for('ehome'))

    session.pop('phone', False)
    form=EmptyForm()
    return render_template('index.html',form=form)

#=================================================register====================

@app.route('/register',methods=['GET','POST'])
def register():
    session.pop('logged-in',False)
    session.pop('phone', False)
    form=RegistrationForm()
    if request.method=='POST':
        if form.validate_on_submit():
            cursor=conn.cursor()
            result=request.form.to_dict()
            result['email']=form.data['email'].lower()

            regdata=[]
            for key,value in result.items():
                if(key=='submit' or key=='cpassword' or key=='csrf_token'):
                    continue
                elif (key=='password'):
                    regdata.append(pbkdf2_sha256.hash(value))
                elif(key!='type'):
                    regdata.append(value)
                else:
                    if(value=='1'):
                        regdata.append(f"A-{result['email']}")
                    else:
                        regdata.append(f"E-{result['email']}")
    
          
            print(f"INSERT INTO register (first_name,last_name,phone,email,typex,password) VALUES {tuple(regdata)}")
            cursor.execute(f"INSERT INTO Register(first_name,last_name,phone,email,typex,password) VALUES {tuple(regdata)}")
            conn.commit()
            form.image.data.save( os.path.join(os.getcwd(), 'static/media/profile_image', form.data['email'].lower()))
            print(result['typex'])
            if(result['typex']=='2'):
            	flash('You have successfully registered')
            	return redirect(url_for('login'))
            else :
                session['onetime']=True
                return redirect(url_for('choosedepartment',email=result['email']))     
        else:
            
            return render_template('register.html',form=form)
    else:
        return render_template('register.html', form=form)

#========================================================department======================================
@app.route('/department',methods=['GET','POST'])
def choosedepartment():
    if (not request.args.get('email')):
        return redirect(url_for('home'))
    if(session.get('onetime')==False):
        flash('URL NOT FOUND','danger')
        return redirect(url_for('home'))

    
    email=request.args.get('email')
    form=DepartmentForm()
    if request.method=='POST':  		
	    	cursor=conn.cursor()
	    	result=request.form.to_dict()
	    	department=result['department']
	    	cursor=conn.cursor()
	    	cursor.execute(f"INSERT INTO department(email,dept) VALUES ('{email}','d{int(department)}')")
	    	conn.commit()
	    	session['onetime']=False
	    	flash('You have successfully registered', 'success')
	    	return redirect(url_for('login'))
    else:
        return render_template('department.html',form=form)


#====================================================login===================================


@app.route('/login',methods=['GET','POST'])
def login():
    session.pop('logged-in',False)
    session.pop('phone',False)
    form=LoginForm()
    if(request.method == 'POST'):
        cursor=conn.cursor()
        result=form.data
        cursor.execute(f"Select password from register where lower(email)='{result['email'].lower()}'")
        a=cursor.fetchone()
        if a is None:
            flash(f"NO ACCOUNT EXISTS WITH THIS USERNAME",'danger')
            return redirect(url_for('register'))
        else:
            dict1 = dataret(result['email'].lower())
            if pbkdf2_sha256.verify(result['password'], a[0]):
                session['email']=result['email'].lower()
                session['logged-in']=True
                session['phone']=dict1['phone']
                session['list']=None
                session['up']=1
                session['username']=dict1['typex']
                filt=session['username'][0].lower()
                srt=0
                if(filt=='1'):
                	flash(u'You were successfully logged in ')
                	srt="ehome"
                	return redirect(url_for('ehome'))
                else:                	
                	flash(u'You were successfully logged in ')
                	srt="ahome"
                	return redirect(url_for('adhome'))


                

            else:
                flash("Incorrect Password!","danger")
                return render_template("login.html",form=form)
    else:

        return render_template('login.html',form=form)
 
#===================================================log out============================


@app.route('/logout', methods=['GET', 'POST'])
def logout():
        session.pop('username', None)
        session.pop('email', None)
        session.pop('logged-in', False)
        session.pop('phone', None)
        session.pop('username', None)
        return redirect(url_for('home'))
#=======================================================profile==================================
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if (not session.get('logged-in')):
        flash('LOGIN TO CONTINUE','danger')
        return redirect(url_for('logout'))


    session['up']=1
    form=EmptyForm()

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], session['email'].lower())
    return render_template('profile.html',dp=full_filename,form=form, dict1=dataret(session['email']))

#===========================================================Admin_Home=============================
@app.route('/adhome', methods=['GET', 'POST'])
def adhome():
	if (not session.get('logged-in')):
	 	flash('LOGIN TO CONTINUE','danger')
	 	return redirect(url_for('logout'))
	if(session['username'][0]=='1'):
		flash('URL NOT FOUND','danger')
		return redirect(url_for('profile'))
	cursor=conn.cursor()
	email=session['email']
	cursor.execute(f"select pid from projec where email='{email}'")
	a=cursor.fetchall()
	allprojects=[]
	for x in a:
		pid=x[0]
		cursor.execute(f"select pid,content,date,deadline from projec where pid={pid}")
		allprojects.append(cursor.fetchone())
	return render_template('adhome.html',projects=allprojects)


#==========================================================Add_project=============================

@app.route('/addproject', methods=['GET', 'POST'])
def addproject():
	if (not session.get('logged-in')):
	 	flash('LOGIN TO CONTINUE','danger')
	 	return redirect(url_for('logout'))
	if(session['username'][0]=='1'):
		flash('URL NOT FOUND','danger')
		return redirect(url_for('profile'))
	cursor=conn.cursor()
	
	form=AddProject()
	if(request.method == 'POST'):
		employees=session['emps']
		
		name=form.data['Name']
		users=form.data['users']
		content=form.data['content']
		deadline=form.data['deadline']
		email=session['email']
		print(users)
		import datetime
		dt=datetime.date.today().isoformat()
		print(f"Insert into projec(name,deadline,date,email,content) values ('{name}','{deadline}','{dt}','{session['email']}','{content}')")
		cursor.execute(f"Insert into projec(name,deadline,date,email,content) values ('{name}','{deadline}','{dt}','{session['email']}','{content}')")
		conn.commit()
		cursor.execute("select max(pid) from projec ")
		pid=cursor.fetchone()
		pid=pid[0]
		pid=int(pid)
		
		for user in users:
			username=employees[int(user)-1].split(' ')[4]
			cursor.execute(f"insert into users(pid,email) values({pid},'{username}')")
			conn.commit()
			
		session.pop('emps',None)
		return redirect(url_for('adhome'))
	else:
		cursor.execute("select first_name,dept,register.email from register inner join department on register.email=department.email")
		a=cursor.fetchall()
		print(a)
		employees=[]

		for x in a:
				nam=x[0]+' of department '+x[1]+'email: '+x[2]
				employees.append(nam)
		
		session['emps']=employees
		employees=enumerate(employees,start=1)
		form.users.choices=employees
		return render_template('addproject.html',form=form)
#==============================================================Employee_Home============================

@app.route('/ehome', methods=['GET', 'POST'])
def ehome():
	if (not session.get('logged-in')):
	 	flash('LOGIN TO CONTINUE','danger')
	 	return redirect(url_for('logout'))
	if(session['username'][0]=='2'):
		flash('URL NOT FOUND','danger')
		return redirect(url_for('profile'))
	cursor=conn.cursor()
	email=session['email']
	cursor.execute(f"select pid from users where email='{email}'")
	a=cursor.fetchall()
	allprojects=[]
	for x in a:
		pid=x[0]
		cursor.execute(f"select pid,first_name,date,deadline from projec join register on projec.email=register.email where pid={pid}")
		allprojects.append(cursor.fetchone())
	return render_template('ehome.html',projects=allprojects)

#==============================================================View_project==========================

@app.route('/viewproject', methods=['GET', 'POST'])
def viewproject():
	if (not session.get('logged-in')):
	 	flash('LOGIN TO CONTINUE','danger')
	 	return redirect(url_for('logout'))
	if(not request.args.get('a')):
		flash('URL NOT FOUND','danger')
		return redirect(url_for('ehome'))
	pid=request.args['a']
	name=request.args['admin']
	cursor=conn.cursor()
	cursor.execute(f"select name,register.first_name,content,date,deadline from projec join register on register.email=projec.email where pid={pid}")
	a=cursor.fetchone()
	return render_template('viewproject.html',project=a)

#================================================system call================
if __name__ == '__main__':
    app.run(debug=True)