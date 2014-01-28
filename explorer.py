from flask import Flask
from flask import render_template
app = Flask(__name__)

ISO639_3_TO_WALS = {
    "aly": ["aly",],
    "aer": ["amp", "arr"],  # Actually maps to two WALS ids... "arr" too!
    "are": ["arr", "awe"],
}

ISO639_3_TO_GLOTTOCODE = {
    "aly": ["alya1239",],
    "aer": ["east2379",],   # only maps to one glottocode
    "are": ["west2441",],
}


def wals_code_list_from_iso639_3(iso639_3):
    return ISO639_3_TO_WALS.get(iso639_3, ())


def glottocode_list_from_iso639_3(iso639_3):
    # Is this ever a list with more than one member?
    return ISO639_3_TO_GLOTTOCODE.get(iso639_3, ())


@app.route('/')
def index():
        return 'Index Page'


@app.route('/language/iso639_3/<iso639_3_code>')
def show_language(iso639_3_code):
    # show the profile for the language
    wals_code_list = wals_code_list_from_iso639_3(iso639_3_code)
    glottocode_list = glottocode_list_from_iso639_3(iso639_3_code)
    return render_template('show_language.html', 
        iso639_3_code=iso639_3_code,
        wals_code_list=wals_code_list,
        glottocode_list=glottocode_list)


if __name__ == "__main__":
        app.run(debug=True)
