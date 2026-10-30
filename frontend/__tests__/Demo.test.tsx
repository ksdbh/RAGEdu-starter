// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import Study from '../components/Study';

const fetchMock = vi.fn<typeof fetch>();
const local = { mode: 'local', courses: [
  { course_id: 'CS101', documents: 1, passages: 2 },
  { course_id: 'BIO101', documents: 1, passages: 1 },
] };
const answer = {
  answer: 'Dijkstra requires nonnegative edge weights.',
  citations: [{ title: 'Graphs', source: 'graphs.pdf', page: 1, snippet: 'Nonnegative edge weights are required.' }],
  metadata: { mode: 'local', status: 'ok' },
};
const response = (data: unknown, status = 200) => new Response(JSON.stringify(data), { status });

beforeEach(() => { vi.stubGlobal('fetch', fetchMock); });
afterEach(() => { cleanup(); vi.unstubAllGlobals(); fetchMock.mockReset(); });
async function ready() {
  await waitFor(() => expect(screen.getByRole('button', { name: 'Ask' })).toHaveProperty('disabled', false));
}

describe('course Q&A', () => {
  test('sends selected course and renders actual page citations', async () => {
    fetchMock.mockResolvedValueOnce(response(local)).mockResolvedValueOnce(response(answer));
    render(<Study />);
    await ready();
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByText('Course excerpts')).toBeTruthy();
    expect(screen.getByText('Source: graphs.pdf')).toBeTruthy();
    expect(screen.getByText('Page: 1')).toBeTruthy();
    expect(screen.getByText('Nonnegative edge weights are required.')).toBeTruthy();
    const payload = JSON.parse(fetchMock.mock.calls[1][1]?.body as string);
    expect(payload.course_id).toBe('CS101');
    expect(fetchMock.mock.calls[1][0]).toBe('/api/backend/rag/answer');
  });

  test('clears previous course evidence when switching courses', async () => {
    fetchMock.mockResolvedValueOnce(response(local)).mockResolvedValueOnce(response(answer));
    render(<Study />);
    await ready();
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    await screen.findByText('Source: graphs.pdf');
    fireEvent.change(screen.getByLabelText('Course'), { target: { value: 'BIO101' } });
    expect(screen.queryByText('Source: graphs.pdf')).toBeNull();
  });

  test('shows insufficient evidence without fabricated citations', async () => {
    fetchMock.mockResolvedValueOnce(response(local)).mockResolvedValueOnce(response({
      answer: 'Not enough context to answer confidently.', citations: [],
      metadata: { mode: 'local', status: 'insufficient_evidence' },
    }));
    render(<Study />);
    await ready();
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByText('More evidence needed')).toBeTruthy();
    expect(screen.getByText('No matching source passages.')).toBeTruthy();
    expect(screen.queryByText('Demo answer')).toBeNull();
  });

  test('disables search when no courses have been ingested', async () => {
    fetchMock.mockResolvedValueOnce(response({ mode: 'local', courses: [] }));
    render(<Study />);
    await screen.findByText(/No course materials yet/);
    expect(screen.getByRole('button', { name: 'Ask' })).toHaveProperty('disabled', true);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('does not silently select demo mode after configuration failure', async () => {
    fetchMock.mockResolvedValueOnce(response({}, 503));
    render(<Study />);
    expect((await screen.findByRole('alert')).textContent).toContain('configuration is unavailable');
    expect(screen.getByRole('button', { name: 'Ask' })).toHaveProperty('disabled', true);
  });

  test('shows request errors and restores the search button', async () => {
    fetchMock.mockResolvedValueOnce(response(local)).mockRejectedValueOnce(new Error('offline'));
    render(<Study />);
    await ready();
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect((await screen.findByRole('alert')).textContent).toContain('offline');
    expect(screen.getByRole('button', { name: 'Ask' })).toHaveProperty('disabled', false);
  });

  test('rejects empty input without making an answer request', async () => {
    fetchMock.mockResolvedValueOnce(response(local));
    render(<Study />);
    await ready();
    fireEvent.change(screen.getByLabelText('Your question'), { target: { value: '   ' } });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(screen.getByRole('alert').textContent).toContain('Please enter a question');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('retains an explicitly labeled demo without a course requirement', async () => {
    fetchMock.mockResolvedValueOnce(response({ mode: 'demo', courses: [] }))
      .mockResolvedValueOnce(response({ ...answer, metadata: { mode: 'demo', status: 'ok' } }));
    render(<Study />);
    await ready();
    expect(screen.getByText(/Answers and sample sources are simulated/)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByText('Demo answer')).toBeTruthy();
    const payload = JSON.parse(fetchMock.mock.calls[1][1]?.body as string);
    expect(payload).not.toHaveProperty('course_id');
  });
});
