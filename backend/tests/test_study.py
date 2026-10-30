import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ingest import ingest_pdf
from test_local_index import write_pdf

client = TestClient(app)


@pytest.fixture
def local_corpus(monkeypatch, tmp_path):
    path = tmp_path / 'corpus.sqlite3'
    monkeypatch.setenv('RAGEDU_MODE', 'local')
    monkeypatch.setenv('RAGEDU_INDEX_PATH', str(path))
    source = write_pdf(tmp_path / 'graphs.pdf', [
        'Dijkstra requires nonnegative edge weights.',
        'Astar uses a heuristic to prioritize graph exploration.',
    ])
    document = ingest_pdf(source, course_id='CS101', index_path=path)
    biology = write_pdf(tmp_path / 'biology.pdf', ['Photosynthesis converts light into chemical energy.'])
    ingest_pdf(biology, course_id='BIO101', index_path=path)
    return path, document


def test_course_api_cites_only_actual_ingested_pages(local_corpus):
    _, document = local_corpus
    response = client.post('/rag/answer', json={'query': 'What does Dijkstra require?', 'course_id': 'CS101', 'top_k': 1})
    assert response.status_code == 200
    data = response.json()
    assert data['metadata']['mode'] == 'local'
    assert data['metadata']['generation'] == 'source_excerpts'
    assert data['metadata']['status'] == 'ok'
    assert len(data['citations']) == 1
    citation = data['citations'][0]
    assert citation['document_id'] == document['document_id']
    assert citation['course_id'] == 'CS101'
    assert citation['source'] == 'graphs.pdf'
    assert citation['page'] == 1
    assert 'nonnegative edge weights' in citation['snippet']
    assert 'nonnegative edge weights' in data['answer']
    assert 'Context A' not in data['answer']


def test_missing_course_never_falls_back_to_demo(local_corpus):
    for course in ['unknown', 'CS101']:
        data = client.post('/rag/answer', json={'query': 'photosynthesis', 'course_id': course}).json()
        assert data['metadata']['status'] == 'insufficient_evidence'
        assert data['citations'] == []
        assert data['metadata']['confidence'] == 0
    assert client.post('/rag/answer', json={'query': 'Dijkstra'}).status_code == 422
    assert client.post('/rag/answer', json={'query': 'Dijkstra', 'course_id': '   '}).status_code == 422


def test_status_lists_courses_without_content(local_corpus):
    status = client.get('/rag/status').json()
    assert status['mode'] == 'local'
    assert status['retrieval'] == 'keyword'
    assert status['generation'] == 'source_excerpts'
    assert status['courses'] == [
        {'course_id': 'BIO101', 'documents': 1, 'passages': 1},
        {'course_id': 'CS101', 'documents': 1, 'passages': 2},
    ]


def test_running_api_sees_newly_ingested_material(local_corpus, tmp_path):
    path, _ = local_corpus
    assert client.post('/rag/answer', json={'query': 'Bellman', 'course_id': 'CS101'}).json()['citations'] == []
    source = write_pdf(tmp_path / 'more.pdf', ['Bellman Ford supports negative edge weights.'])
    ingest_pdf(source, course_id='CS101', index_path=path)
    citation = client.post('/rag/answer', json={'query': 'Bellman', 'course_id': 'CS101'}).json()['citations'][0]
    assert citation['source'] == 'more.pdf'


def test_missing_local_index_returns_empty_status_not_demo(monkeypatch, tmp_path):
    monkeypatch.setenv('RAGEDU_MODE', 'local')
    monkeypatch.setenv('RAGEDU_INDEX_PATH', str(tmp_path / 'missing.sqlite3'))
    assert client.get('/rag/status').json()['courses'] == []
    data = client.post('/rag/answer', json={'query': 'Dijkstra', 'course_id': 'CS101'}).json()
    assert data['metadata']['mode'] == 'local'
    assert data['citations'] == []


def test_corrupt_index_and_invalid_mode_are_unavailable_not_demo(monkeypatch, tmp_path):
    index = tmp_path / 'broken.sqlite3'
    index.write_text('not a database')
    monkeypatch.setenv('RAGEDU_MODE', 'local')
    monkeypatch.setenv('RAGEDU_INDEX_PATH', str(index))
    assert client.get('/rag/status').status_code == 503
    assert client.post('/rag/answer', json={'query': 'Dijkstra', 'course_id': 'CS101'}).status_code == 503
    monkeypatch.setenv('RAGEDU_MODE', 'typo')
    assert client.get('/rag/status').status_code == 503


@pytest.mark.parametrize('payload', [
    {'query': 'a' * 1001}, {'query': 'hello', 'top_k': 21}, {'query': 'hello', 'top_k': True},
    {'query': 'hello', 'question': 'another'},
])
def test_bounded_unambiguous_requests(payload):
    assert client.post('/rag/answer', json=payload).status_code == 422
