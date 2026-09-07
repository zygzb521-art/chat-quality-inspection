<template>
  <div class="chat-replay" ref="chatContainer">
    <div
      v-for="msg in messages"
      :key="msg.id"
      :class="['msg-row', msg.direction === 'agent' ? 'msg-agent' : 'msg-customer']"
    >
      <div class="msg-bubble" :class="{ highlighted: isHighlighted(msg) }">
        <div class="msg-sender">{{ msg.sender_name || (msg.direction === 'agent' ? '客服' : '客户') }}</div>
        <div class="msg-content">{{ msg.content }}</div>
        <div class="msg-time">{{ formatTime(msg.sent_at) }}</div>
      </div>
    </div>
    <div v-if="!messages.length" style="text-align:center;color:#909399;padding:40px">
      暂无消息记录
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'

export interface ChatMessage {
  id: number
  direction: string
  sender_name: string
  content: string
  sent_at: string
}

const props = defineProps<{
  messages: ChatMessage[]
  highlightMsgIds?: number[]
}>()

const chatContainer = ref<HTMLElement>()

function isHighlighted(msg: ChatMessage) {
  return props.highlightMsgIds?.includes(msg.id)
}

function formatTime(t: string) {
  if (!t) return ''
  return t.slice(11, 16)
}

watch(() => props.messages.length, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
})
</script>

<style scoped>
.chat-replay {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.msg-row {
  display: flex;
  margin-bottom: 12px;
}
.msg-agent {
  justify-content: flex-end;
}
.msg-customer {
  justify-content: flex-start;
}
.msg-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.msg-agent .msg-bubble {
  background: #409EFF;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.msg-customer .msg-bubble {
  background: #fff;
  border-bottom-left-radius: 4px;
}
.msg-bubble.highlighted {
  border: 2px solid #f56c6c;
  box-shadow: 0 0 0 2px rgba(245,108,108,0.2);
}
.msg-sender {
  font-size: 11px;
  opacity: 0.7;
  margin-bottom: 4px;
}
.msg-content {
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  white-space: pre-wrap;
}
.msg-time {
  font-size: 11px;
  opacity: 0.5;
  text-align: right;
  margin-top: 4px;
}
</style>