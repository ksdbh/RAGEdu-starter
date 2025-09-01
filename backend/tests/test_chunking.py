from backend.app.ingest import semantic_chunk_text


def test_chunking_short_text():
    text = "This is a short paragraph. It should not be split."
    chunks = semantic_chunk_text(text, max_tokens=200, overlap_tokens=20)
    assert len(chunks) == 1
    assert text in chunks[0].text


def test_chunking_long_text_splits_and_overlaps():
    # Build a long text by repeating sentences
    sentence = "This is a sentence describing an algorithm."
    paragraphs = [" ".join([sentence] * 40), " ".join([sentence] * 20)]
    text = "\n\n".join(paragraphs)

    # Choose small token budget to force splits
    chunks = semantic_chunk_text(text, max_tokens=40, overlap_tokens=10)
    assert len(chunks) >= 2

    # Check overlap: last portion of chunk i should appear at start of chunk i+1
    for i in range(len(chunks) - 1):
        a = chunks[i].text
        b = chunks[i + 1].text
        # Determine overlap length in chars (approximation; overlap uses chars)
        # We expect some shared substring between the end of a and start of b
        overlap_found = False
        max_overlap_check = min(len(a), len(b), 200)
        for L in range(10, max_overlap_check, 10):
            if a.endswith(b[:L]):
                overlap_found = True
                break
        assert overlap_found, f"Expected overlap between chunk {i} and {i+1}.\nA(end): {a[-60:]}\nB(start): {b[:60]}"


def test_chunking_empty_text():
    chunks = semantic_chunk_text("", max_tokens=100)
    assert chunks == []
