from flask import Flask,render_template,request,flash,redirect
from flask_sqlalchemy  import SQLAlchemy
import requests
import string



application=Flask(__name__)
app=application
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'
db=SQLAlchemy(app)

class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50), nullable=False)


@app.route('/',methods=['GET','POST'])
def index():
    cities=City.query.all()
    url="https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=395804698ea1ddb0728ab7a918d6ce8d"
    if request.method=='GET':
        data=[]
        for city in cities:
            r=requests.get(url.format(city.name)).json()

            weather={
            'city':city.name,
            'temperature':r['main']['temp'],
            'description':r['weather'][0]['description'],
            'icon':r['weather'][0]['icon'],
            }
            data.append(weather)
        return render_template('weather.html',data=data)
    elif request.method=='POST':
        err_msg=''
        newcity= request.form.get('city')
        newcity=newcity.lower()
        newcity=string.capwords(newcity)
        if newcity:
            existcity=City.query.filter_by(name=newcity).first()
            if not existcity:
                newcity_data=requests.get(url.format(newcity)).json()
                if newcity_data['cod']==200:
                    newcity_obj=City(name=newcity)
                    db.session.add(newcity_obj)
                    db.session.commit()
                else:
                    err_msg='Not a Valid City'
            else:
                err_msg='City Already Exist'
        if err_msg:
            flash(err_msg,'error')
        else:
            flash('City Added Successfully!','success')
        return redirect('/')
@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()

    db.session.delete(city)
    db.session.commit()

    flash(('Successfully deleted {}!').format(city.name), 'success')
    return redirect('/')
if __name__=='__main__':
    app.run()
