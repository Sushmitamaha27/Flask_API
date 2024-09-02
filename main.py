from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
'''
Install the required packages first:
Open the Terminal in PyCharm (bottom left).

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db' # URI=connection detail
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


    def to_dict(self):
        dictionary={}
        for column in self.__table__.columns:
            dictionary[column.name]=getattr(self,column.name)
        return dictionary

        # return {column.name:getattr(self,column.name) for column in self.__table__.column}

with app.app_context(): #which allows you to interact with the Flask application and its extensions (like SQLAlchemy)
  #application context is set up before the block is executed and properly cleaned up afterward.
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random')
def random_cafe():
    result=db.session.execute(db.select(Cafe))
    all_cafe=result.scalars().all()
    random_cafe=random.choice(all_cafe)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def all_cafe():
    result=db.session.execute(db.select(Cafe))
    all_cafe=result.scalars().all()
    all_cafe_json=[cafe.to_dict() for cafe in all_cafe]
    return jsonify(cafe=all_cafe_json)


@app.route('/search')
def find_cafe():
    para=request.args.get("loc")
    para=para.strip('\'"') # if query parameter is not working proper then we have to remove the presence of extra characters like quotes (" or %22) around the location name
    result=db.session.execute(db.select(Cafe).where(Cafe.location==para))
    all_cafe=result.scalars().all()
    if all_cafe:
        return jsonify(cafe=[cafe.to_dict() for cafe in all_cafe])
    else:
        return jsonify(error={"Not Found":"Sorry, we dont have a cafe at the location"}),404


# HTTP POST - Create Record


# Note:The correct way to access form data from request.form is by using request.form.get('key') or request.form['key']
# Always use request.form.get('key') to access form data to avoid errors.


@app.route('/add',methods=['POST'])
def add_cafe():
        new_cafe=Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success":"Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record

@app.route('/update-price/<cafe_id>',methods=["PATCH"])
def patch_request(cafe_id):
    new_price=request.args.get("new_price")
    cafe=db.get_or_404(Cafe,cafe_id)
    if cafe:
        cafe.coffee_price=new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}),200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),400



# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>',methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key=request.args.get('api-key')
    if api_key=="TopSecretAPIKey":
        cafe=db.get_or_404(Cafe,cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(response={"Sorry cafe_id not present in database"}),404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403




if __name__ == '__main__':
    app.run(debug=True)
