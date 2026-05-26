import React, { useState } from 'react';
import { Send, Upload, Bot, User, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  originalImage?: string;
  aiImage?: string;
  errorCode?: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Merhaba Zeynep! Ben TRtek Akıllı Servis Masası asistanıyım. Karşılaştığın Windows Server veya Oracle DB hata ekran görüntüsünü buraya sürükleyip bırakarak ya da seçerek gönderebilirsin.',
      sender: 'bot',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() && !selectedFile) return;

    const userMessageId = Math.random().toString(36).substring(2, 9);
    const botMessageId = Math.random().toString(36).substring(2, 9);

    const newUserMessage: Message = {
      id: userMessageId,
      text: input || "Görsel analiz ediliyor...",
      sender: 'user',
      timestamp: new Date(),
      originalImage: previewUrl || undefined
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInput('');
    
    const formData = new FormData();
    if (selectedFile) {
      formData.append('file', selectedFile);
    }
    formData.append('userPrompt', input);
    formData.append('userId', '00000000-0000-0000-0000-000000000000'); 

    setLoading(true);
    setSelectedFile(null);
    setPreviewUrl(null);

    try {
      const response = await fetch('http://localhost:5121/api/Ticket/upload-screenshot', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        
        const newBotMessage: Message = {
          id: botMessageId,
          text: data.response,
          sender: 'bot',
          timestamp: new Date(),
          aiImage: data.aiImage || undefined,
          errorCode: data.errorCode !== "UNKNOWN" ? data.errorCode : undefined
        };
        setMessages(prev => [...prev, newBotMessage]);
      } else {
        throw new Error("Sunucu hatası");
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: botMessageId,
        text: '[Sistem Hatası]: API sunucusuna bağlanılamadı.',
        sender: 'bot',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', backgroundColor: '#0f111a', color: 'white', fontFamily: 'sans-serif', overflow: 'hidden' }}>
      
      {/* Sol Panel */}
      <div style={{ width: '320px', backgroundColor: '#151922', padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'between', borderRight: '1px solid #2d3248', boxSizing: 'border-box' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '8px', margin: '0 0 8px 0' }}>
            <ShieldAlert size={20} />
            <span>Görsel Analiz Paneli</span>
          </h2>
          <p style={{ fontSize: '12px', color: '#9ca3af', margin: '0 0 24px 0' }}>Hata içeren ekran görüntüsünü aşağıdaki alana bırakın.</p>
          
          <label style={{ border: '2px dashed #4b5563', borderRadius: '16px', padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center', justify: 'center', cursor: 'pointer', backgroundColor: '#1e2230', height: '240px', boxSizing: 'border-box' }}>
            <input type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} />
            {previewUrl ? (
              <img src={previewUrl} alt="Önizleme" style={{ maxHeight: '100%', maxWidth: '100%', borderRadius: '8px', objectFit: 'contain' }} />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <Upload size={40} style={{ color: '#6b7280', marginBottom: '12px' }} />
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#d1d5db' }}>Resmi buraya sürükleyin veya tıklayın</span>
                <span style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>PNG, JPG desteklenir</span>
              </div>
            )}
          </label>
        </div>
        <div style={{ fontSize: '12px', color: '#4b5563', textAlign: 'center', marginTop: 'auto' }}>TRtek Yazılım Proje Formu v1.0</div>
      </div>

      {/* Sağ Panel (Chat) */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: '#1e2230', height: '100%', overflow: 'hidden' }}>
        
        {/* Mesaj Alanı */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {messages.map((msg) => (
            <div key={msg.id} style={{ display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', maxWidth: '75%', flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row' }}>
                <div style={{ padding: '8px', borderRadius: '50%', backgroundColor: msg.sender === 'user' ? '#3b82f6' : '#2d3248', display: 'flex', alignItems: 'center', justify: 'center', width: '36px', height: '36px', boxSizing: 'border-box' }}>
                  {msg.sender === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div style={{ padding: '16px', borderRadius: '16px', backgroundColor: msg.sender === 'user' ? '#3b82f6' : '#2d3248' }}>
                  
                  {msg.errorCode && (
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', backgroundColor: '#ef4444', color: 'white', fontSize: '11px', fontWeight: 'bold', padding: '4px 8px', borderRadius: '6px', marginBottom: '10px' }}>
                      <CheckCircle2 size={12} />
                      <span>TESPİT EDİLEN HATA: {msg.errorCode}</span>
                    </div>
                  )}

                  <p style={{ fontSize: '14px', lineHeight: '1.5', margin: 0, whiteSpace: 'pre-line' }}>{msg.text}</p>
                  
                  {msg.originalImage && (
                    <img src={msg.originalImage} alt="Yüklenen" style={{ marginTop: '12px', borderRadius: '8px', maxHeight: '240px', objectFit: 'cover', border: '1px solid #4b5563' }} />
                  )}

                  {msg.aiImage && (
                    <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #4b5563' }}>
                      <span style={{ fontSize: '12px', color: '#4ade80', fontWeight: 'bold', display: 'block', marginBottom: '4px' }}>🤖 AI Görsel Analiz Raporu (OpenCV + EasyOCR):</span>
                      <img src={msg.aiImage} alt="AI Processed" style={{ borderRadius: '8px', maxHeight: '240px', objectFit: 'cover', border: '2px solid #22c55e' }} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', justify: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', backgroundColor: '#2d3248', padding: '16px', borderRadius: '16px' }}>
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>Yapay zeka görüntüyü işliyor...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Formu */}
        <form onSubmit={handleSend} style={{ padding: '16px', backgroundColor: '#151922', borderTop: '1px solid #2d3248', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Sorunuzu buraya yazın (Örn: Bu hata nedir?)"
            style={{ flex: 1, backgroundColor: '#1e2230', border: '1px solid #4b5563', borderRadius: '12px', padding: '12px 16px', fontSize: '14px', color: 'white', outline: 'none' }}
          />
          <button type="submit" style={{ backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '12px', padding: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', justify: 'center' }}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
