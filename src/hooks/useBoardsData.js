import { useCallback, useEffect, useRef, useState } from 'react';
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  onSnapshot,
  orderBy,
  query,
  serverTimestamp,
  updateDoc,
  writeBatch,
} from 'firebase/firestore';

import { BOARDS } from '../constants.js';
import { db, firebaseReady } from '../firebase.js';

const emptyState = BOARDS.reduce((acc, board) => ({ ...acc, [board.id]: [] }), {});

const plainTextToHtml = (value = '') =>
  value
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => `<p>${line.replace(/[&<>"']/g, (char) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    })[char])}</p>`)
    .join('') || '<p><br></p>';

export function useBoardsData() {
  const [cards, setCards] = useState(emptyState);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const cardsRef = useRef(emptyState);

  useEffect(() => {
    cardsRef.current = cards;
  }, [cards]);

  useEffect(() => {
    if (!firebaseReady || !db) {
      setError('Firebase is not configured. Update your .env before running the app.');
      setLoading(false);
      return undefined;
    }

    const unsubscribers = BOARDS.map((board) => {
      const q = query(collection(db, 'boards', board.id, 'cards'), orderBy('order', 'asc'));
      return onSnapshot(
        q,
        (snapshot) => {
          setCards((prev) => ({
            ...prev,
            [board.id]: snapshot.docs.map((docSnap) => ({
              id: docSnap.id,
              ...docSnap.data(),
            })),
          }));
          setLoading(false);
        },
        (err) => {
          console.error(err);
          setError(err.message);
          setLoading(false);
        },
      );
    });

    return () => {
      unsubscribers.forEach((unsub) => unsub && unsub());
    };
  }, []);

  const addCard = useCallback(
    async (boardId, rawText) => {
      if (!db) return;
      const target = collection(db, 'boards', boardId, 'cards');
      await addDoc(target, {
        board: boardId,
        content: plainTextToHtml(rawText),
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        order: (cardsRef.current[boardId] || []).length,
      });
    },
    [],
  );

  const updateCardContent = useCallback(async (boardId, cardId, html) => {
    if (!db) return;
    const ref = doc(db, 'boards', boardId, 'cards', cardId);
    await updateDoc(ref, {
      content: html.trim() || '<p><br></p>',
      updatedAt: serverTimestamp(),
    });
  }, []);

  const deleteCard = useCallback(async (boardId, cardId) => {
    if (!db) return;
    await deleteDoc(doc(db, 'boards', boardId, 'cards', cardId));
  }, []);

  const reorderBoard = useCallback(async (boardId, orderedIds) => {
    if (!db || !Array.isArray(orderedIds) || !orderedIds.length) return;
    const batch = writeBatch(db);
    orderedIds.forEach((cardId, index) => {
      const ref = doc(db, 'boards', boardId, 'cards', cardId);
      batch.update(ref, {
        order: index,
        updatedAt: serverTimestamp(),
      });
    });
    await batch.commit();
  }, []);

  const moveCard = useCallback(
    async ({ cardId, fromBoard, toBoard, nextFromOrder, nextToOrder }) => {
      if (!db) return;
      const movingCard = cardsRef.current[fromBoard]?.find((card) => card.id === cardId);
      if (!movingCard) return;
      const batch = writeBatch(db);
      const fromRef = doc(db, 'boards', fromBoard, 'cards', cardId);
      batch.delete(fromRef);

      nextFromOrder.forEach((id, index) => {
        const ref = doc(db, 'boards', fromBoard, 'cards', id);
        batch.update(ref, { order: index, updatedAt: serverTimestamp() });
      });

      const { id: _omit, ...cardPayload } = movingCard;

      nextToOrder.forEach((id, index) => {
        const ref = doc(db, 'boards', toBoard, 'cards', id);
        if (id === cardId) {
          batch.set(ref, {
            ...cardPayload,
            board: toBoard,
            order: index,
            updatedAt: serverTimestamp(),
          });
        } else {
          batch.update(ref, { order: index, updatedAt: serverTimestamp() });
        }
      });

      await batch.commit();
    },
    [],
  );

  return {
    cards,
    loading,
    error,
    addCard,
    updateCardContent,
    deleteCard,
    reorderBoard,
    moveCard,
  };
}
