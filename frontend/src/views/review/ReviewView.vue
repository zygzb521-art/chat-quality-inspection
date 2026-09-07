<template>
  <div class="review-view">
    <el-row :gutter="16">
      <el-col :span="14">
        <el-card>
          <template #header>聊天记录</template>
          <ChatReplay :messages="messages" :highlightMsgIds="[]" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card v-if="violation">
          <template #header>复核操作</template>

          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="违规规则">{{ violation.rule_id_code }} {{ violation.rule_name }}</el-descriptions-item>
            <el-descriptions-item label="客服">{{ violation.employee_name || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="客户">{{ violation.customer_name }}</el-descriptions-item>
            <el-descriptions-item label="原始扣分">
              <span style="color:#f56c6c;font-weight:600">-{{ violation.penalty_points }}</span>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <el-form ref="formRef" :model="form" label-width="90px">
            <el-form-item label="复核结果">
              <el-radio-group v-model="form.action">
                <el-radio value="confirm">确认违规</el-radio>
                <el-radio value="appeal">接受申述</el-radio>
                <el-radio value="close">关闭</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="form.action === 'confirm'" label="调整扣分">
              <el-input-number v-model="form.adjusted_penalty" :min="0" :max="200" />
            </el-form-item>
            <el-form-item label="复核备注">
              <el-input v-model="form.review_notes" type="textarea" :rows="3" placeholder="备注信息" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="handleSubmit">提交复核</el-button>
              <el-button @click="$router.back()">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-if="aiResult" style="margin-top:16px">
          <template #header>AI分析参考</template>
          <div style="font-size:13px">
            <div style="margin-bottom:8px">
              态度评分: <strong :style="{color: (aiResult.attitude_score ?? 0) >= 60 ? '#67C23A' : '#f56c6c'}">{{ aiResult.attitude_score ?? '-' }}</strong>
              &nbsp;|&nbsp;
              技巧评分: <strong :style="{color: (aiResult.skill_score ?? 0) >= 60 ? '#67C23A' : '#f56c6c'}">{{ aiResult.skill_score ?? '-' }}</strong>
            </div>
            <div v-for="(s, i) in aiResult.suggestions" :key="i" class="ai-suggestion">
              {{ i+1 }}. {{ s }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getViolation, reviewViolation, type Violation } from '@/api/violations'
import request from '@/api/request'
import ChatReplay from '@/components/ChatReplay.vue'
import type { ChatMessage } from '@/components/ChatReplay.vue'

const route = useRoute()
const router = useRouter()
const violation = ref<Violation | null>(null)
const messages = ref<ChatMessage[]>([])
const aiResult = ref<any>(null)
const submitting = ref(false)
const formRef = ref()

const form = ref({
  action: 'confirm' as 'confirm' | 'appeal' | 'close',
  adjusted_penalty: 0,
  review_notes: '',
})

async function loadData() {
  const id = Number(route.params.id)
  const res = await getViolation(id)
  violation.value = res.data
  form.value.adjusted_penalty = res.data.penalty_points

  if (res.data.conversation) {
    const convRes = await request.get(`/conversations/${res.data.conversation}/`)
    messages.value = convRes.data.messages || []
  }

  const aiRes = await request.get('/ai/results/', { params: { conversation: res.data.conversation } })
  if (aiRes.data.length) aiResult.value = aiRes.data[0]
}

async function handleSubmit() {
  submitting.value = true
  try {
    const payload: any = { action: form.value.action, review_notes: form.value.review_notes }
    if (form.value.action === 'confirm') {
      payload.adjusted_penalty = form.value.adjusted_penalty
    }
    await reviewViolation(Number(route.params.id), payload)
    ElMessage.success('复核完成')
    router.push('/violations')
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.ai-suggestion {
  padding: 4px 0;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}
.ai-suggestion:last-child { border-bottom: none; }
</style>