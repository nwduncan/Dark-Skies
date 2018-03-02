from flask import Flask, render_template, flash, request
from wtforms import Form, validators, DateField, IntegerField, FloatField
from dark_skies import dark_skies
from datetime import datetime, timedelta

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

datetime_format = '%Y-%m-%d'

class ReusableForm(Form):
    latitude = FloatField('Latitude:', validators=[validators.required(), validators.NumberRange(min=-180, max=180)])
    longitude = FloatField('Longitude:', validators=[validators.required(), validators.NumberRange(min=-90, max=90)])
    start = DateField('Start:', validators=[validators.required()], format=datetime_format)
    end = DateField('End:', validators=[validators.required()], format=datetime_format)
    offset = IntegerField('Offset:', validators=[validators.NumberRange(min=0, max=24)])

@app.route("/", methods=['GET', 'POST'])
def dark_index():

    form = ReusableForm(request.form)

    # create default values for first landing on page
    valid = " is-valid"
    valid = " is-invalid"

    formatting = {
        'latitude': {'highlight': None, 'value': None},
        'latitude': {'highlight': None, 'value': None},
        'longitude': {'highlight': None, 'value': None},
        'start': {'highlight': None, 'value': None},
        'end': {'highlight': None, 'value': None},
        'offset': {'highlight': None, 'value': None}
    }

    if request.method == 'POST':
        # form values
        formatting['latitude']['value'] = request.form['latitude']
        formatting['longitude']['value'] = request.form['longitude']
        formatting['start']['value'] = request.form['start']
        formatting['end']['value'] = request.form['end']
        formatting['offset']['value'] = request.form['offset']

        # initial form value hecks
        print dir(form)
        if form.validate():
            print form.errors
            # further form value checks
            errors = None
            # end date must be after start date and must not be greater than 365 days difference
            # start_dtobj = datetime.strptime(start, datetime_format)
            # end_dtobj = datetime.strptime(end, datetime_format)
            # days = end_dtobj - start_dtobj
            # if not timedelta(days=0) < days < timedelta(days=365):
            # Save the comment here.
            flash("yeeeeeEEE")
        else:
            print form.errors
            message = "Error:"+"  |  ".join([ k+":"+v[0] for k, v in form.errors.iteritems() ])
            flash(message)

    return render_template('dark_skies.html', form=form, formatting=formatting)

if __name__ == "__main__":
    app.run()
