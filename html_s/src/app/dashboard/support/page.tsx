'use client';

import React, { useState } from 'react';
import { Send, Phone, Mail, MapPin, MessageSquare } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button, Input, Textarea } from '@/components/ui';

export default function SupportPage() {
  const [messages, setMessages] = useState([
    { id: 1, from: 'system', text: 'Здравствуйте! Чем можем помочь? Опишите вашу проблему или вопрос.', time: '09:00' },
    { id: 2, from: 'user', text: 'Добрый день. Подскажите, когда будет готов мой автомобиль после ремонта тормозной системы?', time: '09:15' },
    { id: 3, from: 'system', text: 'Ваша заявка REQ-2026-0040 (тормозная система) завершена. Автомобиль А 123 МО 77 готов к выдаче. Обратитесь на пост выдачи в секторе B.', time: '09:18' },
  ]);
  const [newMessage, setNewMessage] = useState('');

  const sendMessage = () => {
    if (!newMessage.trim()) return;
    setMessages([
      ...messages,
      { id: messages.length + 1, from: 'user', text: newMessage, time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) },
    ]);
    setNewMessage('');
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { id: prev.length + 1, from: 'system', text: 'Спасибо за обращение. Диспетчер ответит в ближайшее время.', time: new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) },
      ]);
    }, 1500);
  };

  return (
    <>
      <Header title="Поддержка" subtitle="Связь с диспетчерской службой" />

      <div className="p-4 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat */}
          <div className="lg:col-span-2">
            <Card padding="none" className="flex flex-col h-[600px]">
              <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-brand-600 flex items-center justify-center">
                    <MessageSquare size={16} className="text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">Диспетчерская служба</p>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      <span className="text-xs text-slate-500">Онлайн</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-5 space-y-4">
                {messages.map((msg) => (
                  <div key={msg.id} className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${
                      msg.from === 'user'
                        ? 'bg-brand-600 text-white rounded-br-md'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-bl-md'
                    }`}>
                      <p className="text-sm leading-relaxed">{msg.text}</p>
                      <p className={`text-[10px] mt-1 ${msg.from === 'user' ? 'text-brand-200' : 'text-slate-400'}`}>
                        {msg.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="px-5 py-4 border-t border-slate-100 dark:border-slate-700">
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Введите сообщение..."
                    className="flex-1 input-field"
                  />
                  <Button onClick={sendMessage} size="md">
                    <Send size={16} />
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <Card>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4">Контактная информация</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-brand-50 flex items-center justify-center flex-shrink-0">
                    <Phone size={16} className="text-brand-600" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Телефон диспетчерской</p>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">+7 (495) 123-45-67</p>
                    <p className="text-xs text-slate-400 mt-0.5">Круглосуточно</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-brand-50 flex items-center justify-center flex-shrink-0">
                    <Mail size={16} className="text-brand-600" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Электронная почта</p>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">dispatch@carvix.ru</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-9 h-9 rounded-lg bg-brand-50 flex items-center justify-center flex-shrink-0">
                    <MapPin size={16} className="text-brand-600" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Адрес базы</p>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300">г. Москва, ул. Автомобильная, д. 15</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4">Обратная связь</h3>
              <form className="space-y-3" onSubmit={(e) => e.preventDefault()}>
                <Input label="Тема" placeholder="Кратко опишите вопрос" />
                <Textarea label="Сообщение" placeholder="Подробности обращения..." rows={3} />
                <Button className="w-full" size="sm">Отправить</Button>
              </form>
            </Card>

            <Card>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-3">Режим работы</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Диспетчерская</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">24/7</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Сервисная зона</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">08:00 – 20:00</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Администрация</span>
                  <span className="font-medium text-slate-700 dark:text-slate-300">09:00 – 18:00</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
