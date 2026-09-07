<template>
  <div class="platform-config">
    <!-- 平台配置卡片列表 -->
    <el-row :gutter="16">
      <el-col v-for="p in platforms" :key="p.code" :span="6">
        <el-card shadow="hover" :class="['platform-card', { disabled: !getConfig(p.code)?.is_active }]">
          <div class="platform-header">
            <span class="platform-icon">{{ p.icon }}</span>
            <span class="platform-name">{{ p.label }}</span>
          </div>
          <div class="platform-status">
            <el-tag v-if="getConfig(p.code)" :type="getConfig(p.code)!.is_active ? 'success' : 'info'" size="small">
              {{ getConfig(p.code)!.is_active ? '已配置' : '已禁用' }}
            </el-tag>
            <el-tag v-else type="danger" size="small">未配置</el-tag>
          </div>
          <div class="platform-actions">
            <el-button type="primary" size="small" @click="editConfig(p.code)">
              {{ getConfig(p.code) ? '编辑' : '配置' }}
            </el-button>
            <el-button
              v-if="getConfig(p.code)?.is_active"
              size="small"
              @click="openSyncDialog(p.code)"
            >
              同步
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 配置编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editTitle" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="120px">
        <el-form-item label="启用" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <template v-for="f in currentFields" :key="f.key">
          <el-form-item :label="f.label" :prop="'config_data.' + f.key">
            <el-input
              v-model="form.config_data[f.key]"
              :type="f.secret ? 'password' : 'text'"
              :placeholder="f.placeholder"
              show-password
            />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="editingId" type="danger" @click="handleDelete">删除配置</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 手动同步对话框 -->
    <el-dialog v-model="syncVisible" title="手动同步" width="420px">
      <el-form label-width="80px">
        <el-form-item label="平台">
          <el-tag>{{ platforms.find(p => p.code === syncPlatform)?.label }}</el-tag>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="syncDateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="syncVisible = false">取消</el-button>
        <el-button type="primary" :loading="syncing" @click="handleSync">开始同步</el-button>
      </template>
    </el-dialog>

    <!-- 同步日志 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>同步日志</span>
          <el-button size="small" @click="loadSyncLogs">刷新</el-button>
        </div>
      </template>
      <el-table :data="syncLogs" v-loading="logsLoading" empty-text="暂无同步记录">
        <el-table-column prop="platform_display" label="平台" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
              {{ row.status === 'success' ? '成功' : row.status === 'failed' ? '失败' : '运行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="conversations_pulled" label="会话数" width="80" />
        <el-table-column prop="messages_pulled" label="消息数" width="80" />
        <el-table-column prop="started_at" label="开始时间" width="170" />
        <el-table-column prop="finished_at" label="结束时间" width="170" />
        <el-table-column prop="error_message" label="错误信息" min-width="150" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import {
  getConfigs, createConfig, updateConfig, deleteConfig,
  getSyncLogs, triggerSync,
  type ConnectorConfig, type SyncLog,
} from '@/api/platform'

const PLATFORM_META = [
  { code: 'taobao', label: '淘宝/天猫', icon: '淘' },
  { code: 'jd', label: '京东', icon: '京' },
  { code: 'ali1688', label: '1688', icon: '🍑' },
  { code: 'pdd', label: '拼多多', icon: '拼' },
  { code: 'yunke', label: '云客CRM', icon: '云' },
] as const

const PLATFORM_FIELDS: Record<string, { key: string; label: string; placeholder: string; secret: boolean }[]> = {
  taobao: [
    { key: 'app_key', label: 'AppKey', placeholder: '千牛应用 AppKey', secret: false },
    { key: 'app_secret', label: 'AppSecret', placeholder: '千牛应用 AppSecret', secret: true },
    { key: 'refresh_token', label: 'RefreshToken', placeholder: '卖家授权 refresh_token', secret: true },
    { key: 'seller_nick', label: '卖家昵称', placeholder: '淘宝卖家账号昵称', secret: false },
  ],
  jd: [
    { key: 'app_key', label: 'AppKey', placeholder: 'JOS 应用 AppKey', secret: false },
    { key: 'app_secret', label: 'AppSecret', placeholder: 'JOS 应用 AppSecret', secret: true },
    { key: 'access_token', label: 'AccessToken', placeholder: '商家授权 access_token', secret: true },
    { key: 'shop_id', label: '店铺ID', placeholder: '京东店铺 ID', secret: false },
  ],
  ali1688: [
    { key: 'app_key', label: 'AppKey', placeholder: '1688 应用 AppKey', secret: false },
    { key: 'app_secret', label: 'AppSecret', placeholder: '1688 应用 AppSecret', secret: true },
    { key: 'access_token', label: 'AccessToken', placeholder: '商家授权 access_token', secret: true },
  ],
  pdd: [
    { key: 'seller_account', label: '商家账号', placeholder: '拼多多商家账号', secret: false },
    { key: 'seller_password', label: '商家密码', placeholder: '拼多多商家密码', secret: true },
  ],
  yunke: [
    { key: 'api_key', label: 'API Key', placeholder: '云客CRM API Key', secret: true },
    { key: 'api_secret', label: 'API Secret', placeholder: '云客CRM API Secret', secret: true },
    { key: 'base_url', label: 'API地址', placeholder: 'https://api.yingke.com', secret: false },
  ],
}

const platforms = PLATFORM_META

// Config state
const configs = ref<ConnectorConfig[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const editingPlatform = ref('')
const saving = ref(false)

const formRef = ref<FormInstance>()
const form = ref({
  is_active: true,
  config_data: {} as Record<string, string>,
})

const currentFields = computed(() => PLATFORM_FIELDS[editingPlatform.value] || [])
const editTitle = computed(() => {
  const p = platforms.find(p => p.code === editingPlatform.value)
  return `${editingId.value ? '编辑' : '配置'} — ${p?.label || ''}`
})

// Build validation rules dynamically
const formRules = computed(() => {
  const rules: Record<string, any> = {
    is_active: [],
  }
  for (const f of currentFields.value) {
    rules['config_data.' + f.key] = [
      { required: true, message: `请输入${f.label}`, trigger: 'blur' },
    ]
  }
  return rules
})

function getConfig(code: string): ConnectorConfig | undefined {
  return configs.value.find(c => c.platform === code)
}

function editConfig(code: string) {
  const existing = getConfig(code)
  editingPlatform.value = code
  editingId.value = existing?.id || null
  form.value = {
    is_active: existing?.is_active ?? true,
    config_data: existing?.config_data ? { ...existing.config_data } : {},
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      platform: editingPlatform.value,
      is_active: form.value.is_active,
      config_data: form.value.config_data,
    }
    if (editingId.value) {
      await updateConfig(editingId.value, payload)
      ElMessage.success('配置已更新')
    } else {
      await createConfig(payload)
      ElMessage.success('配置已创建')
    }
    dialogVisible.value = false
    await loadConfigs()
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定删除此平台配置？', '确认', { type: 'warning' })
    if (editingId.value) {
      await deleteConfig(editingId.value)
      ElMessage.success('已删除')
      dialogVisible.value = false
      await loadConfigs()
    }
  } catch {
    // cancelled
  }
}

// Sync state
const syncVisible = ref(false)
const syncPlatform = ref('')
const syncDateRange = ref<[string, string] | null>(null)
const syncing = ref(false)

function openSyncDialog(code: string) {
  syncPlatform.value = code
  const now = new Date()
  const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
  syncDateRange.value = [
    yesterday.toISOString().slice(0, 19).replace('T', ' '),
    now.toISOString().slice(0, 19).replace('T', ' '),
  ]
  syncVisible.value = true
}

async function handleSync() {
  if (!syncDateRange.value) {
    ElMessage.warning('请选择时间范围')
    return
  }
  syncing.value = true
  try {
    await triggerSync({
      platform: syncPlatform.value,
      start_time: syncDateRange.value[0],
      end_time: syncDateRange.value[1],
    })
    ElMessage.success('同步任务已触发')
    syncVisible.value = false
  } finally {
    syncing.value = false
  }
}

// Sync logs
const syncLogs = ref<SyncLog[]>([])
const logsLoading = ref(false)

async function loadSyncLogs() {
  logsLoading.value = true
  try {
    const res = await getSyncLogs()
    syncLogs.value = res.data
  } finally {
    logsLoading.value = false
  }
}

async function loadConfigs() {
  const res = await getConfigs()
  configs.value = res.data
}

onMounted(() => {
  loadConfigs()
  loadSyncLogs()
})
</script>

<style scoped>
.platform-config {
  padding: 4px;
}
.platform-card {
  cursor: default;
  transition: transform 0.2s;
  margin-bottom: 16px;
}
.platform-card.disabled {
  opacity: 0.6;
}
.platform-card:hover {
  transform: translateY(-2px);
}
.platform-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.platform-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #409EFF;
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}
.platform-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}
.platform-status {
  margin-bottom: 12px;
}
.platform-actions {
  display: flex;
  gap: 8px;
}
</style>
