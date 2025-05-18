import os
import tempfile
import pytest
from app import app, UPLOAD_FOLDER, CONVERTED_FOLDER

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'RKNN Toolkit2 Web UI' in rv.data

def test_settings_page(client):
    rv = client.get('/settings')
    assert rv.status_code == 200
    assert b'Settings' in rv.data

def test_files_page(client):
    rv = client.get('/files')
    assert rv.status_code == 200
    assert b'Files' in rv.data

def test_export_page_get(client):
    rv = client.get('/export')
    assert rv.status_code == 200
    assert b'Export' in rv.data

def test_upload_invalid_file(client):
    data = {
        'model_file': (tempfile.NamedTemporaryFile(suffix='.txt'), 'test.txt'),
        'platform': 'rk3576',
        'dtype': 'fp'
    }
    rv = client.post('/export', data=data, content_type='multipart/form-data')
    assert b'Invalid file type' in rv.data or b'No conversion started.' in rv.data

def test_upload_valid_file(client):
    # Create a dummy ONNX file
    dummy_onnx = tempfile.NamedTemporaryFile(suffix='.onnx', delete=False)
    dummy_onnx.write(b'\x08\x01')
    dummy_onnx.close()
    with open(dummy_onnx.name, 'rb') as f:
        data = {
            'model_file': (f, 'dummy.onnx'),
            'platform': 'rk3576',
            'dtype': 'fp'
        }
        rv = client.post('/export', data=data, content_type='multipart/form-data')
        assert b'task_id' in rv.data or b'Conversion started' in rv.data
    os.remove(dummy_onnx.name)

def test_download_and_delete(client):
    # Upload a dummy file
    dummy_onnx = tempfile.NamedTemporaryFile(suffix='.onnx', delete=False)
    dummy_onnx.write(b'\x08\x01')
    dummy_onnx.close()
    filename = os.path.basename(dummy_onnx.name)
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    os.rename(dummy_onnx.name, upload_path)
    # Download
    rv = client.get(f'/download/uploads/{filename}')
    assert rv.status_code == 200
    # Delete
    rv = client.post(f'/delete/uploads/{filename}')
    assert rv.status_code == 302  # Redirect after delete
    assert not os.path.exists(upload_path)
