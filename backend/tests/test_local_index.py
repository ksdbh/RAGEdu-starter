import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

from backend.app.ingest import ingest_pdf, chunk_pages, semantic_chunk_text
from backend.app.local_index import LocalIndex


def write_pdf(path, pages):
    writer = PdfWriter()
    for text in pages:
        page = writer.add_blank_page(width=612, height=792)
        if text:
            font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                     NameObject('/Subtype'): NameObject('/Type1'),
                                     NameObject('/BaseFont'): NameObject('/Helvetica')})
            page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
            content = DecodedStreamObject()
            escaped = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            content.set_data(f'BT /F1 12 Tf 50 700 Td ({escaped}) Tj ET'.encode())
            page[NameObject('/Contents')] = writer._add_object(content)
    with Path(path).open('wb') as stream:
        writer.write(stream)
    return Path(path)


@pytest.fixture
def course_pdf(tmp_path):
    return write_pdf(tmp_path / 'algorithms.pdf', [
        'Dijkstra finds shortest paths with nonnegative edge weights.',
        '',
        'Astar uses a heuristic to guide graph search toward the goal.',
    ])


def test_real_pdf_page_numbers_persist_and_reimport_is_idempotent(course_pdf, tmp_path):
    path = tmp_path / 'corpus.sqlite3'
    first = ingest_pdf(course_pdf, course_id='CS101', index_path=path)
    second = ingest_pdf(course_pdf, course_id='CS101', index_path=path)
    assert first == second
    assert first['pages'] == 3
    assert first['passages'] == 2
    reopened = LocalIndex(path)
    assert reopened.courses() == [{'course_id': 'CS101', 'documents': 1, 'passages': 2}]
    hits = reopened.search('What is Astar?', course_id='CS101')
    assert hits[0]['page'] == 3
    assert hits[0]['source'] == 'algorithms.pdf'
    assert hits[0]['document_id'] == first['document_id']
    assert hits[0]['score'] == 1.0
    assert 'heuristic' in hits[0]['snippet']


def test_cli_ingestion_can_be_read_by_a_new_process(course_pdf, tmp_path):
    path = tmp_path / 'corpus.sqlite3'
    result = subprocess.run([sys.executable, '-m', 'backend.app.ingest', str(course_pdf),
                             '--course', 'CS101', '--index', str(path)], capture_output=True, text=True, check=True)
    document = json.loads(result.stdout)
    env = {**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[2])}
    query = subprocess.run([sys.executable, '-c',
                           'from backend.app.local_index import LocalIndex; import sys; '
                           'print(LocalIndex(sys.argv[1]).search("Dijkstra", course_id="CS101")[0]["document_id"])',
                           str(path)], capture_output=True, text=True, check=True, env=env)
    assert query.stdout.strip() == document['document_id']


def test_course_filter_cannot_match_another_course(course_pdf, tmp_path):
    path = tmp_path / 'corpus.sqlite3'
    ingest_pdf(course_pdf, course_id='CS101', index_path=path)
    other = write_pdf(tmp_path / 'biology.pdf', ['Photosynthesis converts light into chemical energy.'])
    ingest_pdf(other, course_id='BIO101', index_path=path)
    index = LocalIndex(path)
    assert index.search('photosynthesis', course_id='CS101') == []
    assert index.search('Dijkstra', course_id='BIO101') == []
    assert index.search('Dijkstra', course_id="CS101' OR 1=1 --") == []
    assert index.search('quantum', course_id='CS101') == []
    assert index.search('AND OR " * :', course_id='CS101') == []


def test_missing_index_is_not_created_by_read(tmp_path):
    path = tmp_path / 'missing.sqlite3'
    index = LocalIndex(path)
    assert index.courses() == []
    assert index.search('Dijkstra', course_id='CS101') == []
    assert not path.exists()


@pytest.mark.parametrize('kind', ['empty', 'invalid', 'encrypted'])
def test_unusable_pdf_fails_without_creating_index(tmp_path, kind):
    source = tmp_path / 'input.pdf'
    if kind == 'invalid':
        source.write_text('not a pdf')
    elif kind == 'empty':
        write_pdf(source, [''])
    else:
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.encrypt('private')
        with source.open('wb') as stream:
            writer.write(stream)
    index = tmp_path / 'corpus.sqlite3'
    result = subprocess.run([sys.executable, '-m', 'backend.app.ingest', str(source), '--course', 'CS101', '--index', str(index)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert 'Ingestion failed' in result.stderr
    assert not index.exists()


def test_replacement_rolls_back_on_bad_passage(course_pdf, tmp_path):
    path = tmp_path / 'corpus.sqlite3'
    result = ingest_pdf(course_pdf, course_id='CS101', index_path=path)
    index = LocalIndex(path)
    with pytest.raises(KeyError):
        index.replace_document(course_id='CS101', document_id=result['document_id'], source='bad.pdf',
                               title='bad', chunks=[{'text': 'bad', 'metadata': {}}])
    assert index.search('Dijkstra', course_id='CS101')


def test_chunking_bounds_and_invalid_overlap():
    chunks = chunk_pages(['HEADING\n' + 'x' * 1000], course_id='CS101', max_chars=80)
    assert all(len(chunk['text']) <= 80 for chunk in chunks)
    assert ''.join(chunk['text'] for chunk in chunks) == 'HEADING\n' + 'x' * 1000
    with pytest.raises(ValueError):
        semantic_chunk_text('some text', max_tokens=5, overlap_tokens=5)
    with pytest.raises(ValueError):
        chunk_pages(['text'], course_id='CS101', max_chars=0)
