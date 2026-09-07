<template>
  <div class="reports">
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>日报管理</span>
          <el-button type="primary" size="small" :loading="generating" @click="generateReport">生成今日日报</el-button>
        </div>
      </template>
      <el-table :data="reports" v-loading="loading" stripe empty-text="暂无日报">
        <el-table-column prop="report_date" label="日期" width="120" />
        <el-table-column prop="total_conversations" label="会话总数" width="100" align="center" />
        <el-table-column prop="violation_count" label="违规数" width="80" align="center" />
        <el-table-column prop="avg_score" label="平均分" width="80" align="center">
          <template #default="{ row }">{{ row.avg_score }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'sent' ? 'success' : 'info'" size="small">
              {{ row.status === 'sent' ? '已推送' : '待推送' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="160" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row)">查看</el-button>
            <el-button v-if="row.status !== 'sent'" size="small" type="primary" @click="pushReport(row)">推送</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="日报详情" width="700px">
      <div v-if="detail">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="日期">{{ detail.report_date }}</el-descriptions-item>
          <el-descriptions-item label="会话总数">{{ detail.total_conversations }}</el-descriptions-item>
          <el-descriptions-item label="违规数">{{ detail.violation_count }}</el-descriptions-item>
          <el-descriptions-item label="平均分">{{ detail.avg_score }}</el-descriptions-item>
          <el-descriptions-item label="总扣分">{{ detail.total_penalty }}</el-descriptions-item>
          <el-descriptions-item label="高风险会话">{{ detail.high_risk_count }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="section-title">员工排名</div>
        <div v-for="(emp, i) in detail.employee_rankings" :key="i" class="rank-item">
          <span>{{ i + 1 }}. {{ emp.name }} — 违规 {{ emp.count }} 次, 扣 {{ emp.penalty }} 分</span>
        </div>
        <el-divider />
        <div class="section-title">规则分布</div>
        <div v-for="(r, i) in detail.rule_distribution" :key="i" class="rank-item">
          {{ r.name }}: {{ r.count }} 次
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const reports = ref<any[]>([])
const loading = ref(false)
const generating = ref(false)
const detailVisible = ref(false)
const detail = ref<any>(null)

async function loadReports() {
  loading.value = true
  try {
    const res = await request.get('/reports/')
    reports.value = res.data
  } finally {
    loading.value = false
  }
}

async function generateReport() {
  generating.value = true
  try {
    await request.post('/reports/generate/')
    ElMessage.success('日报已生成')
    await loadReports()
  } finally {
    generating.value = false
  }
}

async function viewReport(row: any) {
  const res = await request.get(`/reports/${row.id}/`)
  detail.value = res.data
  detailVisible.value = true
}

async function pushReport(row: any) {
  try {
    await request.post(`/reports/${row.id}/push/`)
    ElMessage.success('已推送')
    await loadReports()
  } catch {
    ElMessage.error('推送失败')
  }
}

onMounted(loadReports)
</script>

<style scoped>
.section-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: #303133;
}
.rank-item {
  padding: 4px 0;
  font-size: 13px;
  color: #606266;
}
</style>