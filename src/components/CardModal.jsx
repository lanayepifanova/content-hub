import { useEffect, useRef } from 'react';

const BLOCK_OPTIONS = [
  { label: 'Paragraph', value: 'p' },
  { label: 'Headline', value: 'h2' },
  { label: 'Subhead', value: 'h3' },
];

const TOOLBAR_ACTIONS = [
  { label: 'B', command: 'bold' },
  { label: 'I', command: 'italic' },
  { label: 'U', command: 'underline' },
  { label: '• List', command: 'insertUnorderedList' },
  { label: '1. List', command: 'insertOrderedList' },
  { label: 'Highlight', command: 'hiliteColor', value: '#fff59d' },
  { label: 'Clear', command: 'removeFormat' },
];

export function CardModal({ open, initialHtml, onClose, onSave }) {
  const editorRef = useRef(null);

  useEffect(() => {
    if (open && editorRef.current) {
      editorRef.current.innerHTML = initialHtml || '<p><br></p>';
      setTimeout(() => {
        editorRef.current?.focus();
      }, 0);
    }
  }, [open, initialHtml]);

  if (!open) return null;

  const execCommand = (command, value = null) => {
    editorRef.current?.focus();
    document.execCommand(command, false, value);
  };

  const handleSave = () => {
    const html = editorRef.current?.innerHTML ?? '<p><br></p>';
    onSave(html);
  };

  return (
    <div className="modal" role="dialog" aria-modal="true">
      <div className="modal-panel">
        <div className="modal-header">
          <h3>Edit card</h3>
          <button type="button" className="ghost" onClick={onClose}>
            &times;
          </button>
        </div>
        <div className="modal-toolbar">
          <select onChange={(event) => execCommand('formatBlock', event.target.value)} defaultValue="p">
            {BLOCK_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {TOOLBAR_ACTIONS.map((action) => (
            <button
              key={action.label}
              type="button"
              onClick={() => execCommand(action.command, action.value)}
            >
              {action.label}
            </button>
          ))}
        </div>
        <div ref={editorRef} className="modal-editor" contentEditable suppressContentEditableWarning />
        <div className="modal-actions">
          <button type="button" className="ghost" onClick={onClose}>
            Close
          </button>
          <button type="button" onClick={handleSave}>
            Save changes
          </button>
        </div>
      </div>
    </div>
  );
}
