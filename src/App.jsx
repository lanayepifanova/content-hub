import { useMemo, useState } from 'react';
import { BOARDS } from './constants.js';
import { Board } from './components/Board.jsx';
import { CardModal } from './components/CardModal.jsx';
import { useBoardsData } from './hooks/useBoardsData.js';

function App() {
  const {
    cards,
    loading,
    error,
    addCard,
    deleteCard,
    reorderBoard,
    moveCard,
    updateCardContent,
  } = useBoardsData();
  const [activeCard, setActiveCard] = useState(null);
  const [dragMeta, setDragMeta] = useState(null);

  const openCard = (boardId, cardId) => {
    setActiveCard({ boardId, cardId });
  };

  const closeModal = () => setActiveCard(null);

  const modalCard = useMemo(() => {
    if (!activeCard) return null;
    return cards[activeCard.boardId]?.find((card) => card.id === activeCard.cardId) ?? null;
  }, [activeCard, cards]);

  const handleSaveModal = async (html) => {
    if (!activeCard) return;
    await updateCardContent(activeCard.boardId, activeCard.cardId, html);
    setActiveCard(null);
  };

  const handleDragStart = (event, boardId, cardId) => {
    setDragMeta({ boardId, cardId });
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
    }
  };

  const handleDragEnd = () => {
    setDragMeta(null);
  };

  const computeDropIndex = (event, boardId) => {
    const list = event.currentTarget;
    if (!list) return cards[boardId]?.length || 0;
    const siblings = Array.from(list.querySelectorAll('[data-card-id]')).filter(
      (node) => node.dataset.cardId !== dragMeta?.cardId,
    );
    const pointerY = event.clientY;
    for (let i = 0; i < siblings.length; i += 1) {
      const rect = siblings[i].getBoundingClientRect();
      if (pointerY < rect.top + rect.height / 2) {
        return i;
      }
    }
    return siblings.length;
  };

  const handleDragOver = (event) => {
    if (!dragMeta) return;
    event.preventDefault();
  };

  const handleDrop = async (event, targetBoardId) => {
    event.preventDefault();
    if (!dragMeta) return;
    const dropIndex = computeDropIndex(event, targetBoardId);
    const targetIds = (cards[targetBoardId] || []).map((card) => card.id);

    if (dragMeta.boardId === targetBoardId) {
      const filtered = targetIds.filter((id) => id !== dragMeta.cardId);
      filtered.splice(dropIndex, 0, dragMeta.cardId);
      if (JSON.stringify(filtered) !== JSON.stringify(targetIds)) {
        await reorderBoard(targetBoardId, filtered);
      }
    } else {
      const fromIds = (cards[dragMeta.boardId] || []).map((card) => card.id).filter((id) => id !== dragMeta.cardId);
      const newTarget = [...targetIds];
      newTarget.splice(dropIndex, 0, dragMeta.cardId);
      await moveCard({
        cardId: dragMeta.cardId,
        fromBoard: dragMeta.boardId,
        toBoard: targetBoardId,
        nextFromOrder: fromIds,
        nextToOrder: newTarget,
      });
    }

    setDragMeta(null);
  };

  return (
    <div className="app-shell">
      <header>
        <h1>Content Hub</h1>
      </header>

      {error && <div className="notice error">{error}</div>}
      {!error && loading && <div className="notice">Connecting to Firebase…</div>}

      <main className="boards">
        {BOARDS.map((board) => (
          <Board
            key={board.id}
            board={board}
            items={cards[board.id]}
            disabled={Boolean(error)}
            onAdd={addCard}
            onOpen={openCard}
            onDelete={handleDelete}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          />
        ))}
      </main>

      <CardModal
        open={Boolean(modalCard)}
        initialHtml={modalCard?.content}
        onClose={closeModal}
        onSave={handleSaveModal}
      />
    </div>
  );

  async function handleDelete(boardId, cardId) {
    await deleteCard(boardId, cardId);
    if (activeCard?.cardId === cardId) {
      setActiveCard(null);
    }
  }
}

export default App;
