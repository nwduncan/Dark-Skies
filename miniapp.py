from flask import Flask, render_template, flash, request
from wtforms import Form, validators, DateField, IntegerField, FloatField

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    latitude = FloatField('Latitude:', validators=[validators.required(), validators.NumberRange(min=-180, max=180)])
    longitude = FloatField('Longitude:', validators=[validators.required(), validators.NumberRange(min=-90, max=90)])
    start = DateField('Start:', validators=[validators.required()], format='%Y-%m-%d')
    end = DateField('End:', validators=[validators.required()], format='%Y-%m-%d')
    offset = IntegerField('Offset:', validators=[validators.required(), validators.NumberRange(min=0, max=24)])

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)

    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        start = request.form['start']
        end = request.form['end']
        offset = request.form['offset']

        print latitude, " ", longitude, " ", start, " ", type(end), " ", offset

        if form.validate():
            # Save the comment here.
            flash(latitude+" "+longitude+" "+start+" "+end+" "+offset)
        else:
            print form.errors
            flash('Error: All the form fields are required. \n{}'.format(form.errors))

    return render_template('hello.html', form=form)

if __name__ == "__main__":
    app.run()
