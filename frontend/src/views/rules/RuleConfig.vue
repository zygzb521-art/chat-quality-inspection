<template>
  <div class="rule-config">
    <el-row :gutter="16">
      <el-col v-for="cat in categories" :key="cat.code" :span="8">
        <el-card>
          <template #header>
            <span style="font-weight: 500">{{ cat.name }}</span>
            <el-tag size="small" style="margin-left: 8px">
              {{ groupedRules[cat.code]?.length || 0 }} 条规则
            </el-tag>
          </template>
          <div v-for="rule in groupedRules[cat.code] || []" :key="rule.rule_id" class="rule-item" @click="editRule(rule)">
            <div class="rule-header">
              <span class="rule-id">{{ rule.rule_id }}</span>
              <span class="rule-name">{{ rule.name }}</span>
              <el-tag :type="ruleTypeTag(rule.rule_type)" size="small">{{ ruleTypeLabel(rule.rule_type) }}</el-tag>
            </div>
            <div class="rule-desc">{{ rule.description }}</div>
            <div class="rule-meta">
              <span>扣分: {{ rule.first_penalty }}/{{ rule.second_penalty }}/{{ rule.third_penalty }}/{{ rule.fourth_penalty }}</span>
              <el-switch v-model="rule.is_active" size="small" @change="toggleActive(rule)" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="'编辑 — ' + editingRule?.rule_id + ' ' + editingRule?.name" width="600px" destroy-on-close>
      <el-form v-if="editingRule" ref="formRef" :model="editForm" label-width="110px">
        <el-form-item label="规则描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editForm.is_active" />
        </el-form-item>
        <el-divider content-position="left">阶梯扣分</el-divider>
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="首次" label-width="40px">
              <el-input-number v-model="editForm.first_penalty" :min="0" :max="200" size="small" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="二次" label-width="40px">
              <el-input-number v-model="editForm.second_penalty" :min="0" :max="200" size="small" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="三次" label-width="40px">
              <el-input-number v-model="editForm.third_penalty" :min="0" :max="200" size="small" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="四次" label-width="40px">
              <el-input-number v-model="editForm.fourth_penalty" :min="0" :max="200" size="small" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider v-if="editingRule.rule_type === 'keyword'" content-position="left">关键词配置</el-divider>
        <el-form-item v-if="editingRule.rule_type === 'keyword'" label="关键词">
          <el-select v-model="editForm.config.keywords" multiple filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="kw in editForm.config.keywords" :key="kw" :label="kw" :value="kw" />
          </el-select>
          <div class="form-tip">输入关键词后回车添加</div>
        </el-form-item>
        <el-divider v-if="editingRule.rule_type === 'timing'" content-position="left">时间参数</el-divider>
        <el-form-item v-if="editingRule.rule_type === 'timing'" label="超时(分钟)">
          <el-input-number v-model="editForm.config.timeout_minutes" :min="1" :max="1440" />
        </el-form-item>
        <el-form-item v-if="editingRule.rule_type === 'ai'" label="提示">
          <div class="form-tip">AI类规则由大模型分析执行，阈值在后续版本中配置</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { getRules, updateRule, getCategories, type Rule, type RuleCategory } from '@/api/rules'

const rules = ref<Rule[]>([])
const categories = ref<RuleCategory[]>([])
const dialogVisible = ref(false)
const editingRule = ref<Rule | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()

const editForm = ref({
  description: '',
  is_active: true,
  first_penalty: 20,
  second_penalty: 30,
  third_penalty: 40,
  fourth_penalty: 50,
  config: {} as Record<string, any>,
})

const groupedRules = computed(() => {
  const map: Record<string, Rule[]> = {}
  for (const rule of rules.value) {
    const code = rule.category_code
    if (!map[code]) map[code] = []
    map[code].push(rule)
  }
  return map
})

const RULE_TYPE_MAP: Record<string, string> = {
  keyword: '关键词',
  timing: '时间',
  ai: 'AI',
  hybrid: '混合',
}

function ruleTypeLabel(t: string) {
  return RULE_TYPE_MAP[t] || t
}

function ruleTypeTag(t: string) {
  return t === 'ai' ? 'warning' : t === 'timing' ? 'info' : t === 'hybrid' ? 'danger' : 'success'
}

function editRule(rule: Rule) {
  editingRule.value = rule
  editForm.value = {
    description: rule.description,
    is_active: rule.is_active,
    first_penalty: rule.first_penalty,
    second_penalty: rule.second_penalty,
    third_penalty: rule.third_penalty,
    fourth_penalty: rule.fourth_penalty,
    config: JSON.parse(JSON.stringify(rule.config)),
  }
  dialogVisible.value = true
}

async function toggleActive(rule: Rule) {
  try {
    await updateRule(rule.id, { is_active: rule.is_active })
    ElMessage.success(rule.is_active ? '已启用' : '已禁用')
  } catch {
    rule.is_active = !rule.is_active
  }
}

async function handleSave() {
  if (!editingRule.value) return
  saving.value = true
  try {
    await updateRule(editingRule.value.id, {
      description: editForm.value.description,
      is_active: editForm.value.is_active,
      first_penalty: editForm.value.first_penalty,
      second_penalty: editForm.value.second_penalty,
      third_penalty: editForm.value.third_penalty,
      fourth_penalty: editForm.value.fourth_penalty,
      config: editForm.value.config,
    })
    ElMessage.success('规则已更新')
    dialogVisible.value = false
    await loadRules()
  } finally {
    saving.value = false
  }
}

async function loadRules() {
  const res = await getRules()
  rules.value = res.data
}

async function loadCategories() {
  const res = await getCategories()
  categories.value = res.data
}

onMounted(() => {
  loadRules()
  loadCategories()
})
</script>

<style scoped>
.rule-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}
.rule-item:last-child {
  border-bottom: none;
}
.rule-item:hover {
  background: #fafafa;
  margin: 0 -16px;
  padding: 10px 16px;
}
.rule-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
.rule-id {
  color: #409EFF;
  font-weight: 600;
  font-size: 13px;
  min-width: 40px;
}
.rule-name {
  font-size: 13px;
  color: #303133;
  flex: 1;
}
.rule-desc {
  font-size: 12px;
  color: #909399;
  margin: 4px 0;
  padding-left: 40px;
  line-height: 1.4;
}
.rule-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
  padding-left: 40px;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>