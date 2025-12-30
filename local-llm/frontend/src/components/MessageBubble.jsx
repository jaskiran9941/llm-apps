import React from 'react';

export default function MessageBubble({ role, content }) {
    const isUser = role === 'user';
    return (
        <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none shadow-sm'
                    }`}
            >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>
            </div>
        </div>
    );
}
