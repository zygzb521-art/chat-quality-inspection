<template>
  <div class="ranking">
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>员工排名（扣分越少排名越前）</span>
          <el-radio-group v-model="period" size="small" @change="loadRanking">
            <el-radio-button value="week">本周</el-radio-button>
            <el-radio-button value="month">本月</el-radio-button>
            <el-radio-button value="all">全部</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table :data="rankings" v-loading="loading" stripe empty-text="暂无排名数据">
        <el-table-column label="排名" width="70" align="center">
          <template #default="{ $index }">
            <el-tag v-if="$index === 0" type="success" round>1</el-tag>
            <el-tag v-else-if="$index === 1" type="warning" round>2</el-tag>
            <el-tag v-else-if="$index === 2" round>3</el-tag>
            <span v-else>{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="客服" width="120" />
        <el-table-column prop="violation_count" label="违规次数" width="100" align="center" />
        <el-table-column prop="total_penalty" label="总扣分" width="100" align="center">
          <template #default="{ row }">
            <span :style="{color: row.total_penalty > 100 ? '#f56c6c' : '#606266', fontWeight: 600}">
              -{{ row.total_penalty }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="评级" min-width="120">
          <template #default="{ row }">
            <el-tag v-if="row.total_penalty === 0" type="success">优秀</el-tag>
            <el-tag v-else-if="row.total_penalty < 40" type="info">良好</el-tag>
            <el-tag v-else-if="row.total_penalty < 100" type="warning">待改进</el-tag>
            <el-tag v-else type="danger">重点关注</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/api/request'

const period = ref('week')
const rankings = ref<any[]>([])
const loading = ref(false)

async function loadRanking() {
  loading.value = true
  try {
    const res = await request.get('/dashboard/ranking/', { params: { period: period.value } })
    rankings.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadRanking)
</script>