<template>
  <div class="violation-list">
    <!-- 筛选栏 -->
    <el-card style="margin-bottom: 16px">
      <el-form :inline="true" :model="filters" size="small">
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部" style="width: 120px">
            <el-option label="待处理" value="pending" />
            <el-option label="已申述" value="appealed" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="客户名称" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadViolations">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 违规列表 -->
    <el-card>
      <el-table :data="violations" v-loading="loading" empty-text="暂无违规记录" stripe>
        <el-table-column prop="rule_id_code" label="规则" width="80" />
        <el-table-column prop="rule_name" label="违规项" min-width="160" />
        <el-table-column prop="customer_name" label="客户" width="120" />
        <el-table-column prop="employee_name" label="客服" width="100" />
        <el-table-column prop="platform" label="平台" width="80">
          <template #default="{ row }">
            {{ platformLabel(row.platform) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="penalty_points" label="扣分" width="70" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600">-{{ row.adjusted_penalty ?? row.penalty_points }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
            <el-button v-if="row.status === 'pending'" type="warning" link size="small" @click="goReview(row)">复核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getViolations, type Violation } from '@/api/violations'

const router = useRouter()
const violations = ref<Violation[]>([])
const loading = ref(false)

const filters = ref({
  status: '',
  search: '',
})

const PLATFORM_LABEL: Record<string, string> = {
  taobao: '淘宝', jd: '京东', ali1688: '1688', pdd: '拼多多', yunke: '云客',
}

function platformLabel(code: string) {
  return PLATFORM_LABEL[code] || code
}

function statusTag(status: string) {
  return status === 'pending' ? 'danger' : status === 'appealed' ? 'warning' : status === 'confirmed' ? 'info' : 'success'
}

async function loadViolations() {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    const res = await getViolations(params)
    violations.value = res.data
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.value = { status: '', search: '' }
  loadViolations()
}

function viewDetail(row: Violation) {
  router.push(`/violations/${row.id}`)
}

function goReview(row: Violation) {
  router.push(`/review/${row.id}`)
}

onMounted(loadViolations)
</script>