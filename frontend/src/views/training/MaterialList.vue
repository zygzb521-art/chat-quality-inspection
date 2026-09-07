<template>
  <div class="training">
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>培训素材</span>
          <el-button type="primary" size="small" @click="openEdit()">新建素材</el-button>
        </div>
      </template>
      <el-table :data="materials" v-loading="loading" stripe empty-text="暂无培训素材">
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="rule_name" label="关联规则" width="120" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'high' ? 'danger' : row.priority === 'medium' ? 'warning' : 'info'" size="small">
              {{ row.priority === 'high' ? '高' : row.priority === 'medium' ? '中' : '低' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_published" label="发布" width="60">
          <template #default="{ row }">{{ row.is_published ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑素材' : '新建素材'" width="650px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="服务态度" value="服务态度" />
            <el-option label="销售技巧" value="销售技巧" />
            <el-option label="执行规范" value="执行规范" />
            <el-option label="产品知识" value="产品知识" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联规则">
          <el-select v-model="form.rule" clearable filterable style="width:100%">
            <el-option v-for="r in rules" :key="r.id" :label="`${r.rule_id} ${r.name}`" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio value="high">高</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="发布">
          <el-switch v-model="form.is_published" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="8" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import request from '@/api/request'

const materials = ref<any[]>([])
const rules = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const formRef = ref<FormInstance>()

const form = ref({
  title: '', content: '', category: '', rule: null, priority: 'medium', is_published: true,
})

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

async function loadMaterials() {
  loading.value = true
  try {
    const res = await request.get('/training/')
    materials.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadRules() {
  const res = await request.get('/rules/')
  rules.value = res.data
}

function openEdit(item?: any) {
  if (item) {
    editingId.value = item.id
    form.value = {
      title: item.title, content: item.content, category: item.category,
      rule: item.rule, priority: item.priority, is_published: item.is_published,
    }
  } else {
    editingId.value = null
    form.value = { title: '', content: '', category: '', rule: null, priority: 'medium', is_published: true }
  }
  dialogVisible.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (editingId.value) {
      await request.put(`/training/${editingId.value}/`, form.value)
      ElMessage.success('已更新')
    } else {
      await request.post('/training/', form.value)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    await loadMaterials()
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确认删除？', '确认')
    await request.delete(`/training/${row.id}/`)
    ElMessage.success('已删除')
    await loadMaterials()
  } catch {}
}

onMounted(() => { loadMaterials(); loadRules() })
</script>