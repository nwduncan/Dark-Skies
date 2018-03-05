from flask import Flask, render_template, flash, request, Markup
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
    results = ""

    # create default values for first landing on page
    formatting = {
        'latitude': {'highlight': "", 'value': None},
        'latitude': {'highlight': "", 'value': None},
        'longitude': {'highlight': "", 'value': None},
        'start': {'highlight': "", 'value': None},
        'end': {'highlight': "", 'value': None},
        'offset': {'highlight': "", 'value': None}
    }

    if request.method == 'POST':
        # form values
        formatting['latitude']['value'] = request.form['latitude']
        formatting['longitude']['value'] = request.form['longitude']
        formatting['start']['value'] = request.form['start']
        formatting['end']['value'] = request.form['end']
        formatting['offset']['value'] = request.form['offset']

        # initial form value hecks
        if form.validate():

            formatting['latitude']['highlight'] = ' is-valid'
            formatting['longitude']['highlight'] = ' is-valid'
            formatting['start']['highlight'] = ' is-valid'
            formatting['end']['highlight'] = ' is-valid'
            formatting['offset']['highlight'] = ' is-valid'


            # further form value checks
            # end date must be after start date and must not be greater than 365 days difference
            start_dtobj = datetime.strptime(request.form['start'], datetime_format)
            end_dtobj = datetime.strptime(request.form['end'], datetime_format)
            days = end_dtobj - start_dtobj
            if days < timedelta(days=1):
                message = 'Error: End date must be after start date'
                formatting['start']['highlight'] = ' is-invalid'
                formatting['end']['highlight'] = ' is-invalid'
            elif timedelta(days=366) < days:
                message = 'Error: Maximum length of one year exceeded'
                formatting['start']['highlight'] = ' is-invalid'
                formatting['end']['highlight'] = ' is-invalid'
            else:
                message = "Calculated."
                results = dark_skies(start_dtobj, end_dtobj, int(formatting['offset']['value']))

            flash(message)
        else:
            print form.errors
            message = "Error:"+", ".join([ k+":"+v[0] for k, v in form.errors.iteritems() ])
            flash(message)

    return render_template('dark_skies.html', form=form, formatting=formatting, results=results)

if __name__ == "__main__":
    app.run()
