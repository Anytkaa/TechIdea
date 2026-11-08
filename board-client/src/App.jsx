import { useState, useEffect, useRef } from 'react';
import { Quickdraw } from '@quickdrawjs/react';
import '@quickdrawjs/core/quickdraw.css';

// Базовый адрес Django-сервера
const DJANGO_API_URL = 'http://localhost:8000';

export default function App() {
  const params = new URLSearchParams(window.location.search);
  
  // Получаем список проектов из URL (передан из Django)
  const projectsParam = params.get('projects');
  const initialProjects = projectsParam ? JSON.parse(decodeURIComponent(projectsParam)) : [];
  
  const currentProjectId = params.get('current') || (initialProjects[0]?.id?.toString() || '1');

  const [projects] = useState(initialProjects);
  const [currentProject, setCurrentProject] = useState(currentProjectId);
  const [socket, setSocket] = useState(null);
  const [loadedSnapshot, setLoadedSnapshot] = useState(undefined);

  // 1. Загружаем снимок из базы при смене проекта
  useEffect(() => {
    if (!currentProject) return;
    
    fetch(`${DJANGO_API_URL}/api/project/${currentProject}/load-board/`, {
      credentials: 'include', // Отправляем cookies (сессию)
    })
      .then(res => {
        if (!res.ok) throw new Error('Ошибка загрузки доски');
        return res.json();
      })
      .then(data => {
        setLoadedSnapshot(data.snapshot || undefined);
      })
      .catch(err => console.error('Ошибка загрузки:', err));
  }, [currentProject]);

  // 2. Подключаемся к WebSocket
  useEffect(() => {
    if (!currentProject) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/quickdraw/${currentProject}/`);
    
    ws.onopen = () => console.log('Quickdraw WS connected');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Применяем изменения от других участников
      // (Если Quickdraw поддерживает applyDiff, можно добавить сюда)
    };

    setSocket(ws);
    return () => ws.close();
  }, [currentProject]);

  // 3. Сохраняем на сервер при изменениях (с задержкой, чтобы не спамить)
  const saveTimeout = useRef(null);
  const handleChange = (diff, source, editor) => {
    if (source !== 'user') return;
    
    // Отправляем изменения через WebSocket (для реального времени)
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(diff));
    }

    // Сохраняем в базу с задержкой (debounce)
    clearTimeout(saveTimeout.current);
    saveTimeout.current = setTimeout(() => {
      fetch(`${DJANGO_API_URL}/api/project/${currentProject}/save-board/`, {
        method: 'POST',
        credentials: 'include', // Отправляем cookies (сессию)
        headers: {
            'Content-Type': 'application/json', 
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ snapshot: editor.store.getSnapshot() })
      }).catch(err => console.error('Ошибка сохранения:', err));
    }, 2000); // Сохраняем через 2 секунды после последнего изменения
  };

  const handleProjectChange = (e) => {
    const newId = e.target.value;
    setCurrentProject(newId);
    // Обновляем URL, чтобы при перезагрузке остаться на этом же проекте
    const newUrl = `?projects=${encodeURIComponent(projectsParam)}&current=${newId}`;
    window.history.pushState({}, '', newUrl);
  };

  if (!projects.length) {
    return <div style={{ padding: '2rem', textAlign: 'center', fontFamily: 'sans-serif' }}>У вас нет доступных проектов.</div>;
  }

  return (
    <div style={{ position: 'fixed', inset: 0, display: 'flex', flexDirection: 'column' }}>
      
      {/* Панель переключения проектов */}
      <div style={{ 
        padding: '10px 20px', 
        background: '#fff', 
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <label style={{ fontWeight: 'bold' }}>Проект:</label>
        <select 
          value={currentProject} 
          onChange={handleProjectChange}
          style={{ padding: '5px 10px', borderRadius: '4px', border: '1px solid #ccc', outline: 'none' }}
        >
          {projects.map(p => (
            <option key={p.id} value={p.id}>{p.title}</option>
          ))}
        </select>
      </div>

      {/* Сама доска */}
      <div style={{ flex: 1, position: 'relative' }}>
        <Quickdraw 
          key={currentProject} // <--- Перерисовываем при смене проекта
          snapshot={loadedSnapshot} // <--- Загружаем сохраненные данные при открытии
          theme="light" 
          grid="lines" 
          watermark={false} 
          onChange={handleChange}
        />
      </div>
    </div>
  );
}

// Вспомогательная функция для получения CSRF-токена
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}