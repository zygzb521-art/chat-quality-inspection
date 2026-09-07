import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '质检看板' },
      },
      {
        path: 'violations',
        name: 'ViolationList',
        component: () => import('@/views/violations/ViolationList.vue'),
        meta: { title: '违规记录' },
      },
      {
        path: 'violations/:id',
        name: 'ViolationDetail',
        component: () => import('@/views/violations/ViolationDetail.vue'),
        meta: { title: '违规详情' },
      },
      {
        path: 'review/:id',
        name: 'ConversationReview',
        component: () => import('@/views/review/ReviewView.vue'),
        meta: { title: '质检复核' },
      },
      {
        path: 'ranking',
        name: 'EmployeeRanking',
        component: () => import('@/views/ranking/EmployeeRanking.vue'),
        meta: { title: '员工排名' },
      },
      {
        path: 'reports',
        name: 'DailyReport',
        component: () => import('@/views/reports/DailyReport.vue'),
        meta: { title: '日报管理' },
      },
      {
        path: 'training',
        name: 'MaterialList',
        component: () => import('@/views/training/MaterialList.vue'),
        meta: { title: '培训素材' },
      },
      {
        path: 'admin/rules',
        name: 'RuleConfig',
        component: () => import('@/views/rules/RuleConfig.vue'),
        meta: { title: '规则配置', roles: ['super_admin'] },
      },
      {
        path: 'admin/platforms',
        name: 'PlatformConfig',
        component: () => import('@/views/platforms/PlatformConfig.vue'),
        meta: { title: '平台配置', roles: ['super_admin'] },
      },
      {
        path: 'admin/employees',
        name: 'EmployeeList',
        component: () => import('@/views/employees/EmployeeList.vue'),
        meta: { title: '员工管理', roles: ['super_admin', 'cs_manager'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router