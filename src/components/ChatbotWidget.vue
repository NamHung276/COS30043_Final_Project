<script setup>
import { ref, nextTick, onMounted } from 'vue';
import { backendApi } from '../services/api';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const renderMarkdown = (text) => {
  return DOMPurify.sanitize(marked.parse(text));
};

const isOpen = ref(false);
const isTyping = ref(false);
const newMessage = ref('');
const messages = ref([
  { role: 'assistant', content: 'Hi there! I am the GameHub AI Assistant. Ask me anything about gaming, news, or deals.' }
]);
const messagesContainer = ref(null);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    scrollToBottom();
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const sendMessage = async () => {
  if (!newMessage.value.trim()) return;

  const userMessage = newMessage.value;
  messages.value.push({ role: 'user', content: userMessage });
  newMessage.value = '';
  isTyping.value = true;
  scrollToBottom();

  try {
    const history = messages.value.slice(0, -1).map(msg => ({ role: msg.role, content: msg.content }));
    const response = await backendApi.post('/chatbot/chat', {
      message: userMessage,
      history: history
    });

    messages.value.push({ role: 'assistant', content: response.data.response });
  } catch (error) {
    messages.value.push({ role: 'assistant', content: 'Oops, something went wrong connecting to my brain. Please try again later.' });
    console.error('Chatbot error:', error);
  } finally {
    isTyping.value = false;
    scrollToBottom();
  }
};

onMounted(() => {
  // Can load initial state from local storage here if needed for session persistence
});
</script>

<template>
  <div class="chatbot-wrapper">
    <!-- Chat Widget Button -->
    <button 
      class="chatbot-toggle-btn" 
      @click="toggleChat" 
      :class="{ 'is-active': isOpen }"
      aria-label="Toggle Chatbot"
    >
      <span v-if="!isOpen">💬</span>
      <span v-else>✕</span>
    </button>

    <!-- Chat Window -->
    <transition name="chat-slide">
      <div v-if="isOpen" class="chatbot-window glass-panel">
        <div class="chatbot-header">
          <div class="header-info">
            <span class="bot-avatar">🤖</span>
            <div class="header-text">
              <h3>GameHub AI</h3>
              <span class="status">Online</span>
            </div>
          </div>
          <button class="close-btn" @click="toggleChat" aria-label="Close Chat">✕</button>
        </div>

        <div class="chatbot-messages" ref="messagesContainer">
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            class="message-wrapper"
            :class="msg.role === 'user' ? 'message-user' : 'message-assistant'"
          >
            <div class="message-bubble" :class="{ 'glass-bubble': msg.role === 'assistant' }">
              <template v-if="msg.role === 'assistant'">
                <div class="markdown-content" v-html="renderMarkdown(msg.content)"></div>
              </template>
              <template v-else>
                {{ msg.content }}
              </template>
            </div>
          </div>
          <div v-if="isTyping" class="message-wrapper message-assistant">
            <div class="message-bubble typing-indicator glass-bubble">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <div class="chatbot-input">
          <input 
            v-model="newMessage" 
            @keyup.enter="sendMessage" 
            type="text" 
            placeholder="Type a message..." 
            :disabled="isTyping"
          />
          <button @click="sendMessage" :disabled="isTyping || !newMessage.trim()" class="send-btn">
            ➤
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  bottom: 6rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chatbot-toggle-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), #ff4d94);
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(255, 51, 102, 0.4);
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chatbot-toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(255, 51, 102, 0.6);
}

.chatbot-toggle-btn.is-active {
  transform: rotate(90deg);
  background: var(--color-background-soft);
  color: var(--color-text);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.chatbot-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 350px;
  height: 500px;
  background: rgba(30, 30, 35, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  transform-origin: bottom right;
}

.chatbot-header {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bot-avatar {
  font-size: 1.8rem;
  background: rgba(255, 51, 102, 0.2);
  border-radius: 50%;
  padding: 8px;
}

.header-text h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.header-text .status {
  font-size: 0.8rem;
  color: #4ade80;
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-text .status::before {
  content: '';
  display: block;
  width: 6px;
  height: 6px;
  background: #4ade80;
  border-radius: 50%;
}

.close-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 1.2rem;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: var(--color-text);
}

.chatbot-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.chatbot-messages::-webkit-scrollbar {
  width: 6px;
}

.chatbot-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.message-wrapper {
  display: flex;
  width: 100%;
}

.message-user {
  justify-content: flex-end;
}

.message-assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 0.95rem;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-user .message-bubble {
  background: linear-gradient(135deg, var(--color-primary), #ff4d94);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-assistant .message-bubble {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text);
  border-bottom-left-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Markdown Styling */
.markdown-content :deep(p) {
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}
.markdown-content :deep(ul), .markdown-content :deep(ol) {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
}
.markdown-content :deep(li) {
  margin-bottom: 0.25rem;
}
.markdown-content :deep(strong) {
  color: var(--color-primary);
}
.markdown-content :deep(h1), .markdown-content :deep(h2), .markdown-content :deep(h3) {
  font-size: 1.1rem;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.chatbot-input {
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  gap: 8px;
}

.chatbot-input input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 10px 16px;
  color: var(--color-text);
  font-size: 0.95rem;
  transition: all 0.3s ease;
  outline: none;
}

.chatbot-input input:focus {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(255, 51, 102, 0.2);
}

.chatbot-input input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  background: #ff4d94;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--color-background-mute);
}

/* Typing Indicator Animation */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 14px 18px;
  align-items: center;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--color-text-muted);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Transitions */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}
</style>
