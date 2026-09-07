<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">今日质检会话</div>
            <div class="stat-value">{{ stats.today_total }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">违规会话</div>
            <div class="stat-value" style="color: #F56C6C">{{ stats.today_violations }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">待复核</div>
            <div class="stat-value" style="color: #E6A23C">{{ stats.pending_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-label">平均分</div>
            <div class="stat-value" style="color: #67C23A">{{ stats.avg_score }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>质检趋势（近7天）</template>
          <v-chart v-if="trendData.length" :option="trendOption" style="height:300px" autoresize />
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>违规分布</template>
          <v-chart v-if="distData.length" :option="distOption" style="height:300px" autoresize />
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>最近违规记录</template>
      <el-table :data="stats.recent_violations" v-if="stats.recent_violations?.length" stripe empty-text="暂无违规">
        <el-table-column label="规则" width="80">
          <template #default="{ row }">{{ row.rule_id }}</template>
        </el-table-column>
        <el-table-column prop="rule_name" label="违规项" min-width="160" />
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="employee_name" label="客服" width="100" />
        <el-table-column prop="penalty" label="扣分" width="70">
          <template #default="{ row }"><span style="color:#f56c6c">-{{ row.penalty }}</span></template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'danger' : 'info'" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="120" />
      </el-table>
      <el-empty v-else description="暂无违规记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'

const stats = ref({
  today_total: 0,
  today_violations: 0,
  pending_count: 0,
  avg_score: 100,
  trend: [] as any[],
  distribution: [] as any[],
  recent_violations: [] as any[],
})

const trendData = computed(() => stats.value.trend || [])
const distData = computed(() => stats.value.distribution || [])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['会话数', '违规数'] },
  grid: { left: 40, right: 20, bottom: 30 },
  xAxis: { type: 'category', data: trendData.value.map((d: any) => d.date) },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      name: '会话数',
      type: 'line',
      smooth: true,
      data: trendData.value.map((d: any) => d.conversations),
      itemStyle: { color: '#409EFF' },
    },
    {
      name: '违规数',
      type: 'line',
      smooth: true,
      data: trendData.value.map((d: any) => d.violations),
      itemStyle: { color: '#F56C6C' },
    },
  ],
}))

const distOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  series: [{
    type: 'pie',
    radius: ['30%', '60%'],
    data: distData.value.map((d: any) => ({
      name: d.rule__category__name,
      value: d.count,
    })),
    label: { show: true, formatter: '{b}\n{d}%' },
  }],
}))

async function loadStats() {
  const res = await request.get('/dashboard/stats/')
  stats.value = res.data
}

onMounted(loadStats)
</script>

<style scoped>
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}
</style>