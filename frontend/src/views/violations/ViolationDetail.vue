<template>
  <div class="violation-detail">
    <el-card v-if="violation">
      <template #header>
        <div style="display:flex;align-items:center;gap:12px">
          <el-button @click="$router.back()">返回</el-button>
          <span style="font-weight:500">违规详情 #{{ violation.id }}</span>
          <el-tag :type="statusTag" size="small">{{ violation.status_display }}</el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border style="margin-bottom:20px">
        <el-descriptions-item label="规则">{{ violation.rule_id_code }} {{ violation.rule_name }}</el-descriptions-item>
        <el-descriptions-item label="扣分" >
          <span style="color:#f56c6c;font-weight:600">-{{ violation.adjusted_penalty ?? violation.penalty_points }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="客服">{{ violation.employee_name || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ violation.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="平台">{{ violation.platform }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ violation.created_at }}</el-descriptions-item>
      </el-descriptions>

      <el-form-item label="违规证据">
        <el-input type="textarea" :model-value="violation.evidence_text" readonly :rows="2" />
      </el-form-item>
    </el-card>

    <el-card style="margin-top:16px">
      <template #header>聊天记录</template>
      <ChatReplay :messages="messages" :highlightMsgIds="[]" />
    </el-card>

    <el-card v-if="aiResult" style="margin-top:16px">
      <template #header>AI分析结果</template>
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="态度评分">
          <span :style="{color: aiResult.attitude_score && aiResult.attitude_score >= 60 ? '#67C23A' : '#f56c6c'}">
            {{ aiResult.attitude_score ?? '-' }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="技巧评分">
          <span :style="{color: aiResult.skill_score && aiResult.skill_score >= 60 ? '#67C23A' : '#f56c6c'}">
            {{ aiResult.skill_score ?? '-' }}
          </span>
        </el-descriptions-item>
      </el-descriptions>
      <div v-if="aiResult.suggestions?.length" style="margin-top:12px">
        <div v-for="(s, i) in aiResult.suggestions" :key="i" class="suggestion-item">
          {{ i + 1 }}. {{ s }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getViolation, type Violation } from '@/api/violations'
import request from '@/api/request'
import ChatReplay from '@/components/ChatReplay.vue'
import type { ChatMessage } from '@/components/ChatReplay.vue'

const route = useRoute()
const violation = ref<Violation | null>(null)
const messages = ref<ChatMessage[]>([])
const aiResult = ref<any>(null)
const loading = ref(true)

const statusTag = computed(() => {
  const map: Record<string, string> = { pending: 'danger', appealed: 'warning', confirmed: 'info', closed: 'success' }
  return map[violation.value?.status || ''] || 'info'
})

async function loadData() {
  const id = Number(route.params.id)
  const res = await getViolation(id)
  violation.value = res.data

  // Fetch conversation messages
  if (res.data.conversation) {
    const convRes = await request.get(`/conversations/${res.data.conversation}/`)
    messages.value = convRes.data.messages || []
  }

  // Fetch AI results
  const aiRes = await request.get('/ai/results/', { params: { conversation: res.data.conversation } })
  if (aiRes.data.length) {
    aiResult.value = aiRes.data[0]
  }
}

onMounted(loadData)
</script>

<style scoped>
.suggestion-item {
  padding: 6px 0;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
}
.suggestion-item:last-child { border-bottom: none; }
</style>