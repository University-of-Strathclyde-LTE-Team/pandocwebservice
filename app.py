from flask import Flask, request, jsonify, send_file
import pypandoc
import os
import uuid
from celery import Celery
import hashlib


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@celery.task
def convert_file_task(file_path, input_format, output_format):
    try:
        output_path = os.path.splitext(file_path)[0] + '.' + output_format
        with open(file_path, 'r', encoding='latin') as file:
            pypandoc.convert_file(file_path, 'latex', outputfile=output_path, extra_args=[])
            print(f"Outputting to {output_path}")
            return {'status': 'completed', 'output_path': output_path}
    except Exception as e:
        print(e)
        return {'status': 'failed', 'error': str(e)}
    

@app.route('/convert', methods=['POST'])
def convert_file():
    input_format = request.form.get('input_format')
    output_format = request.form.get('output_format')
    file = request.files['file']

    if not input_format or not output_format or not file:
        return jsonify({'error': 'Missing required parameters'}), 400
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id+'.'+input_format)
    file.save(file_path)
    output_path = file_path + '.' + output_format
    
    # pypandoc.logger.setLevel('DEBUG')
    with open(file_path, 'r', encoding='latin') as file:
        task = convert_file_task.apply_async(args=[file_path, input_format, output_format])
    return jsonify({'file_id': file_id, 'task_id': task.id})

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    task = convert_file_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'status': 'pending'}
    elif task.state == 'SUCCESS':
        response = {'status': 'completed', 'result': task.result}
    else:
        response = {'status': 'failed', 'error': str(task.info)}
    return jsonify(response)

@app.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    task = convert_file_task.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        result = task.result
        if result['status'] == 'completed':
            output_path = result['output_path']
            if os.path.exists(output_path):
                return send_file(output_path, as_attachment=True)
            else:
                return jsonify({'error': 'File not found'}), 404
        else:
            return jsonify({'error': 'Conversion failed', 'details': result['error']}), 500
    else:
        return jsonify({'error': 'Task not completed or does not exist'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
