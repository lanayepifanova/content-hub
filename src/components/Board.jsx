import { useState } from 'react';
import { relativeTime } from '../utils.js';

export function Board({
  board,
  items = [],
  disabled,
  onAdd,
  onOpen,
  onDelete,
  onDragStart,
  onDragEnd,
  onDragOver,
  onDrop,
}) {
  const [draft, setDraft] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!draft.trim() || disabled) return;
    await onAdd(board.id, draft);
    setDraft('');
  };

  return (
    <section className="board" data-board={board.id}>
      <h2>{board.label}</h2>
      <form className="idea-form" onSubmit={handleSubmit}>
        <textarea
          name="idea"
          placeholder={board.placeholder}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          disabled={disabled}
        />
        <button type="submit" disabled={disabled}>
          Add card
        </button>
      </form>
      <div className="board-list" data-board-list={board.id} onDragOver={onDragOver} onDrop={(event) => onDrop(event, board.id)}>
        {!items.length && <div className="empty">Nothing here yet. Drop your next idea.</div>}
        {items.map((card) => (
          <article
            key={card.id}
            className="idea-card"
            data-card-id={card.id}
            draggable={!disabled}
            onDragStart={(event) => onDragStart(event, board.id, card.id)}
            onDragEnd={onDragEnd}
          >
            <div
              className="card-preview"
              dangerouslySetInnerHTML={{ __html: card.content }}
            />
            <footer>
              <small>{relativeTime(card.updatedAt)}</small>
              <div className="card-actions">
                <button type="button" data-action="open" onClick={() => onOpen(board.id, card.id)}>
                  Open
                </button>
                <button
                  type="button"
                  className="ghost"
                  onClick={() => onDelete(board.id, card.id)}
                >
                  Delete
                </button>
              </div>
            </footer>
          </article>
        ))}
      </div>
    </section>
  );
}
