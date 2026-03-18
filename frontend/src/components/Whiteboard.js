import React, { useRef, useEffect, useState, useCallback } from 'react';

function Whiteboard({ initialImage, onSave }) {
  const canvasRef = useRef(null);
  const tracesCanvasRef = useRef(null);
  const containerRef = useRef(null);

  const [ctx, setCtx] = useState(null);
  const [tracesCtx, setTracesCtx] = useState(null);
  const [drawing, setDrawing] = useState(false);
  const [color, setColor] = useState('black');
  const [brushSize, setBrushSize] = useState(3);
  const [eraserMode, setEraserMode] = useState(false);
  const [undoStack, setUndoStack] = useState([]);
  const [imageObjects, setImageObjects] = useState([]);
  const [selectedImageIndex, setSelectedImageIndex] = useState(-1);
  const [isDragging, setIsDragging] = useState(false);
  const [dragType, setDragType] = useState(null);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [dragStartProps, setDragStartProps] = useState({ x: 0, y: 0, scale: 1 });
  const [eraserIndicator, setEraserIndicator] = useState({ visible: false, x: 0, y: 0 });
  const [backgroundImage, setBackgroundImage] = useState(null);

  const BITMAP_WIDTH = 1000;
  const BITMAP_HEIGHT = 2000;
  const HANDLE_SIZE = 15;

  // Salva estado dos traços
  const saveTracesState = useCallback((context = tracesCtx) => {
    if (!context) return;
    const imageData = context.getImageData(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT);
    setUndoStack(prev => [...prev, imageData].slice(-20));
  }, [tracesCtx]);

  // Redesenha todas as imagens (fundos e objetos)
  const redrawAllImages = useCallback(() => {
    if (!ctx) return;
    if (backgroundImage) {
      ctx.drawImage(
        backgroundImage.img,
        backgroundImage.x,
        backgroundImage.y,
        backgroundImage.width,
        backgroundImage.height
      );
    }
    for (let obj of imageObjects) {
      const width = obj.originalWidth * obj.scale;
      const height = obj.originalHeight * obj.scale;
      ctx.drawImage(obj.img, obj.x, obj.y, width, height);
    }
    if (selectedImageIndex >= 0 && selectedImageIndex < imageObjects.length) {
      const obj = imageObjects[selectedImageIndex];
      const width = obj.originalWidth * obj.scale;
      const height = obj.originalHeight * obj.scale;
      ctx.strokeStyle = 'blue';
      ctx.lineWidth = 2;
      ctx.strokeRect(obj.x, obj.y, width, height);
      ctx.fillStyle = 'blue';
      ctx.fillRect(obj.x - HANDLE_SIZE/2, obj.y - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
      ctx.fillRect(obj.x + width - HANDLE_SIZE/2, obj.y - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
      ctx.fillRect(obj.x - HANDLE_SIZE/2, obj.y + height - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
      ctx.fillRect(obj.x + width - HANDLE_SIZE/2, obj.y + height - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
    }
  }, [ctx, backgroundImage, imageObjects, selectedImageIndex]);

  // Redesenho completo (fundo + traços + imagens)
  const fullRedraw = useCallback(() => {
    if (!ctx || !tracesCtx) return;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT);
    ctx.drawImage(tracesCanvasRef.current, 0, 0);
    redrawAllImages();
  }, [ctx, tracesCtx, redrawAllImages]);

  const undo = useCallback(() => {
    if (undoStack.length > 1) {
      const newStack = [...undoStack];
      newStack.pop();
      setUndoStack(newStack);
      tracesCtx.putImageData(newStack[newStack.length - 1], 0, 0);
      fullRedraw();
    }
  }, [undoStack, tracesCtx, fullRedraw]);

  // Converte coordenadas da tela para coordenadas do bitmap
  const getCanvasCoords = useCallback((e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = BITMAP_WIDTH / rect.width;
    const scaleY = BITMAP_HEIGHT / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;
    return { x, y };
  }, []);

  // Inicialização dos canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    canvas.width = BITMAP_WIDTH;
    canvas.height = BITMAP_HEIGHT;
    const context = canvas.getContext('2d');
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT);
    setCtx(context);

    const tracesCanvas = tracesCanvasRef.current;
    tracesCanvas.width = BITMAP_WIDTH;
    tracesCanvas.height = BITMAP_HEIGHT;
    const tracesContext = tracesCanvas.getContext('2d');
    tracesContext.fillStyle = '#ffffff';
    tracesContext.fillRect(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT);
    setTracesCtx(tracesContext);

    if (initialImage) {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = initialImage;
      img.onload = () => {
        const scale = Math.min(
          BITMAP_WIDTH / img.width,
          BITMAP_HEIGHT / img.height,
          1
        );
        const width = img.width * scale;
        const height = img.height * scale;
        const x = (BITMAP_WIDTH - width) / 2;
        const y = (BITMAP_HEIGHT - height) / 2;
        setBackgroundImage({ img, x, y, width, height });
        context.drawImage(img, x, y, width, height);
        saveTracesState(tracesContext);
      };
    } else {
      saveTracesState(tracesContext);
    }

    // Força foco no canvas
    canvas.focus();
  }, [initialImage, saveTracesState]);

  // Redesenha sempre que algo muda
  useEffect(() => {
    fullRedraw();
  }, [imageObjects, selectedImageIndex, undoStack, backgroundImage, fullRedraw]);

  // Handlers de eventos (com logs para depuração)
  const handlePointerDown = useCallback((e) => {
    e.preventDefault();
    console.log('Pointer down');
    e.target.setPointerCapture(e.pointerId);
    const coords = getCanvasCoords(e);

    // Verifica clique em imagens (código existente)
    let hitIndex = -1;
    let hitType = null;
    for (let i = imageObjects.length - 1; i >= 0; i--) {
      const obj = imageObjects[i];
      const w = obj.originalWidth * obj.scale;
      const h = obj.originalHeight * obj.scale;

      if (i === selectedImageIndex) {
        if (Math.abs(coords.x - obj.x) < HANDLE_SIZE && Math.abs(coords.y - obj.y) < HANDLE_SIZE) {
          hitType = 'resize-tl'; hitIndex = i; break;
        } else if (Math.abs(coords.x - (obj.x + w)) < HANDLE_SIZE && Math.abs(coords.y - obj.y) < HANDLE_SIZE) {
          hitType = 'resize-tr'; hitIndex = i; break;
        } else if (Math.abs(coords.x - obj.x) < HANDLE_SIZE && Math.abs(coords.y - (obj.y + h)) < HANDLE_SIZE) {
          hitType = 'resize-bl'; hitIndex = i; break;
        } else if (Math.abs(coords.x - (obj.x + w)) < HANDLE_SIZE && Math.abs(coords.y - (obj.y + h)) < HANDLE_SIZE) {
          hitType = 'resize-br'; hitIndex = i; break;
        } else if (coords.x >= obj.x && coords.x <= obj.x + w && coords.y >= obj.y && coords.y <= obj.y + h) {
          hitType = 'move'; hitIndex = i; break;
        }
      } else {
        if (coords.x >= obj.x && coords.x <= obj.x + w && coords.y >= obj.y && coords.y <= obj.y + h) {
          hitType = 'select'; hitIndex = i; break;
        }
      }
    }

    if (hitIndex !== -1) {
      setSelectedImageIndex(hitIndex);
      if (hitType !== 'select') {
        setIsDragging(true);
        setDragType(hitType);
        setDragStart(coords);
        const obj = imageObjects[hitIndex];
        setDragStartProps({ x: obj.x, y: obj.y, scale: obj.scale });
      }
      return;
    }

    if (selectedImageIndex !== -1) {
      setSelectedImageIndex(-1);
    }

    if (!tracesCtx) {
      console.error('tracesCtx não disponível');
      return;
    }

    setDrawing(true);
    tracesCtx.beginPath();
    tracesCtx.moveTo(coords.x, coords.y);
    tracesCtx.strokeStyle = eraserMode ? '#ffffff' : color;
    tracesCtx.lineWidth = brushSize;
    tracesCtx.lineCap = 'round';
    tracesCtx.lineJoin = 'round';
  }, [imageObjects, selectedImageIndex, getCanvasCoords, tracesCtx, eraserMode, color, brushSize]);

  const handlePointerMove = useCallback((e) => {
    e.preventDefault();
    const coords = getCanvasCoords(e);

    if (isDragging && selectedImageIndex >= 0) {
      const obj = imageObjects[selectedImageIndex];
      const dx = coords.x - dragStart.x;
      const dy = coords.y - dragStart.y;

      // Lógica de redimensionamento/movimento (existente)
      if (dragType === 'move') {
        obj.x = dragStartProps.x + dx;
        obj.y = dragStartProps.y + dy;
      } else if (dragType === 'resize-br') {
        const newWidth = Math.max(10, (obj.originalWidth * dragStartProps.scale) + dx);
        obj.scale = newWidth / obj.originalWidth;
      } else if (dragType === 'resize-tr') {
        const newWidth = Math.max(10, (obj.originalWidth * dragStartProps.scale) + dx);
        obj.scale = newWidth / obj.originalWidth;
        obj.y = dragStartProps.y + dy;
      } else if (dragType === 'resize-bl') {
        const newHeight = Math.max(10, (obj.originalHeight * dragStartProps.scale) + dy);
        obj.scale = newHeight / obj.originalHeight;
        obj.x = dragStartProps.x + dx;
      } else if (dragType === 'resize-tl') {
        const newWidth = Math.max(10, (obj.originalWidth * dragStartProps.scale) - dx);
        const newHeight = Math.max(10, (obj.originalHeight * dragStartProps.scale) - dy);
        obj.scale = Math.min(newWidth / obj.originalWidth, newHeight / obj.originalHeight);
        obj.x = dragStartProps.x + (obj.originalWidth * dragStartProps.scale - obj.originalWidth * obj.scale);
        obj.y = dragStartProps.y + (obj.originalHeight * dragStartProps.scale - obj.originalHeight * obj.scale);
      }

      fullRedraw();
      return;
    }

    if (drawing && tracesCtx) {
      tracesCtx.strokeStyle = eraserMode ? '#ffffff' : color;
      tracesCtx.lineWidth = brushSize;
      tracesCtx.lineTo(coords.x, coords.y);
      tracesCtx.stroke();
      tracesCtx.beginPath();
      tracesCtx.moveTo(coords.x, coords.y);
      fullRedraw();
    }

    if (eraserMode) {
      setEraserIndicator({ visible: true, x: e.clientX, y: e.clientY });
    } else {
      setEraserIndicator({ visible: false, x: 0, y: 0 });
    }
  }, [isDragging, selectedImageIndex, imageObjects, dragStart, dragType, dragStartProps, fullRedraw, drawing, tracesCtx, eraserMode, color, brushSize, getCanvasCoords]);

  const handlePointerUp = useCallback((e) => {
    e.preventDefault();
    if (isDragging) {
      setImageObjects([...imageObjects]);
      setIsDragging(false);
      setDragType(null);
    }
    if (drawing) {
      setDrawing(false);
      tracesCtx.closePath();
      saveTracesState();
      fullRedraw();
    }
    e.target.releasePointerCapture(e.pointerId);
  }, [isDragging, drawing, imageObjects, tracesCtx, saveTracesState, fullRedraw]);

  const handlePointerLeave = useCallback((e) => {
    handlePointerUp(e);
    setEraserIndicator({ visible: false, x: 0, y: 0 });
  }, [handlePointerUp]);

  // Ações existentes (clear, paste, delete, save)
  const clearCanvas = useCallback(() => {
    tracesCtx.fillStyle = '#ffffff';
    tracesCtx.fillRect(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT);
    saveTracesState();
    setImageObjects([]);
    setSelectedImageIndex(-1);
    fullRedraw();
  }, [tracesCtx, saveTracesState, fullRedraw]);

  const pasteImage = useCallback(async () => {
    try {
      const clipboardItems = await navigator.clipboard.read();
      let imageBlob = null;
      for (const item of clipboardItems) {
        if (item.types.some(type => type.startsWith('image/'))) {
          const imageType = item.types.find(type => type.startsWith('image/'));
          imageBlob = await item.getType(imageType);
          break;
        }
      }
      if (!imageBlob) {
        alert('Nenhuma imagem encontrada na área de transferência.');
        return;
      }
      const img = new Image();
      const url = URL.createObjectURL(imageBlob);
      img.onload = () => {
        const maxWidth = BITMAP_WIDTH * 0.8;
        const maxHeight = BITMAP_HEIGHT * 0.8;
        const scale = Math.min(maxWidth / img.width, maxHeight / img.height, 1);
        const x = (BITMAP_WIDTH - img.width * scale) / 2;
        const y = (BITMAP_HEIGHT - img.height * scale) / 2;
        const newObj = {
          img,
          originalWidth: img.width,
          originalHeight: img.height,
          x, y, scale
        };
        setImageObjects(prev => {
          const newArray = [...prev, newObj];
          setSelectedImageIndex(prev.length);
          return newArray;
        });
      };
      img.onerror = () => {
        alert('Erro ao carregar a imagem colada.');
        URL.revokeObjectURL(url);
      };
      img.src = url;
    } catch (err) {
      alert('Erro ao colar imagem. Verifique as permissões.');
      console.error(err);
    }
  }, []);

  const deleteSelectedImage = useCallback(() => {
    if (selectedImageIndex >= 0) {
      setImageObjects(prev => prev.filter((_, i) => i !== selectedImageIndex));
      setSelectedImageIndex(-1);
    }
  }, [selectedImageIndex]);

  const handleSave = useCallback(() => {
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = BITMAP_WIDTH;
    tempCanvas.height = BITMAP_HEIGHT;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.fillStyle = '#ffffff';
    tempCtx.fillRect(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT);
    if (backgroundImage) {
      tempCtx.drawImage(
        backgroundImage.img,
        backgroundImage.x,
        backgroundImage.y,
        backgroundImage.width,
        backgroundImage.height
      );
    }
    tempCtx.drawImage(tracesCanvasRef.current, 0, 0);
    imageObjects.forEach(obj => {
      const w = obj.originalWidth * obj.scale;
      const h = obj.originalHeight * obj.scale;
      tempCtx.drawImage(obj.img, obj.x, obj.y, w, h);
    });
    const dataURL = tempCanvas.toDataURL('image/png');
    onSave(dataURL);
  }, [backgroundImage, imageObjects, onSave]);

  // Atalhos de teclado
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        undo();
      }
      if (e.key === 'Delete' && selectedImageIndex >= 0) {
        e.preventDefault();
        deleteSelectedImage();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, deleteSelectedImage, selectedImageIndex]);

  useEffect(() => {
    const handleGlobalPaste = (e) => {
      if (containerRef.current && containerRef.current.offsetParent !== null) {
        e.preventDefault();
        pasteImage();
      }
    };
    window.addEventListener('paste', handleGlobalPaste);
    return () => window.removeEventListener('paste', handleGlobalPaste);
  }, [pasteImage]);

  return (
    <div>
      <div
        ref={containerRef}
        className="whiteboard-container"
        style={{ overflow: 'auto', width: '100%', maxHeight: 'calc(100vh - 300px)' }}
      >
        <canvas
          ref={tracesCanvasRef}
          style={{ display: 'none' }}
        />
        <canvas
          ref={canvasRef}
          tabIndex="0"
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerLeave}
          style={{
            display: 'block',
            width: '100%',
            height: 'auto',
            touchAction: 'none',
            cursor: 'crosshair',
            minHeight: '400px', // Garante altura mínima para interação
            backgroundColor: '#fff',
            border: '1px solid #ccc'
          }}
        />
      </div>
      <div className="whiteboard-controls">
        <button onClick={() => { setColor('black'); setEraserMode(false); }}>⚫ Preto</button>
        <button onClick={() => { setColor('red'); setEraserMode(false); }}>🔴 Vermelho</button>
        <button onClick={() => { setColor('blue'); setEraserMode(false); }}>🔵 Azul</button>
        <button onClick={() => { setColor('green'); setEraserMode(false); }}>🟢 Verde</button>
        <button onClick={() => setEraserMode(true)}>🧽 Borracha</button>
        <button onClick={clearCanvas}>🗑️ Limpar tudo</button>
        <button onClick={handleSave}>💾 Salvar Quadro</button>
        <button onClick={pasteImage}>📋 Colar imagem</button>
        <button onClick={deleteSelectedImage} disabled={selectedImageIndex === -1}>
          🗑️ Deletar imagem selecionada
        </button>
        <div className="eraser-size-control">
          <label htmlFor="eraserSize">Tamanho: {brushSize}px</label>
          <input
            type="range"
            id="eraserSize"
            min="1"
            max="50"
            value={brushSize}
            onChange={(e) => setBrushSize(parseInt(e.target.value))}
          />
        </div>
      </div>
      <div className="whiteboard-instructions">
        <small>
          Desenhe com a caneta ou mouse. Use Ctrl+Z para desfazer traços. Para colar imagem, use Ctrl+V.
          Clique em uma imagem para selecionar; arraste nos cantos para redimensionar, no centro para mover.
          Delete remove a imagem selecionada.
        </small>
      </div>
      {eraserMode && eraserIndicator.visible && (
        <div
          style={{
            position: 'fixed',
            left: eraserIndicator.x - brushSize / 2,
            top: eraserIndicator.y - brushSize / 2,
            width: brushSize,
            height: brushSize,
            backgroundColor: 'rgba(255,255,255,0.5)',
            border: '2px solid black',
            pointerEvents: 'none',
            zIndex: 1000,
          }}
        />
      )}
    </div>
  );
}

export default Whiteboard;