from flask import Flask, render_template, jsonify, request
from main import google_sheets
from driver import create_driver

app = Flask(__name__)

processing = False
driver = create_driver()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        global processing
        if processing:
            return jsonify({
                'status_code': 102,
                'error_message': 'There is still a process. Please try again later'
            })
        processing = True
        global driver
        try:
            sheet_id = request.json['sheetId']
            image_count = int(request.json['imageCount'])
            submission_title = request.json['submissionTitle']
            presentation_url = google_sheets(driver, sheet_id, submission_title, image_count)
            processing = False
            return jsonify({
                'status_code': 200,
                'presentation_url': presentation_url
            })

        except Exception as ex:
            print(ex)
            processing = False
            return jsonify({
                'status_code': 500,
                'error_message': 'There was an error. Please try again'
            })
    
        



if __name__ == '__main__':
    app.run()
