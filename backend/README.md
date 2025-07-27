# 学生健康管理系统 - 后端 API 文档

## 项目概述

基于 Django + Django REST Framework 开发的学生健康管理系统后端 API，提供用户注册、登录等基础功能。

## 技术栈

- **框架**: Django 5.2.4
- **API**: Django REST Framework
- **数据库**: SQLite3 (开发环境)
- **密码加密**: Django 内置 hashers
- **跨域支持**: django-cors-headers

## 项目结构

```
backend/
├── manage.py                    # Django 管理脚本
├── db.sqlite3                   # SQLite 数据库文件
├── 学生健康管理系统/             # 主项目目录
│   ├── settings.py              # 项目配置
│   ├── urls.py                  # 主路由配置
│   └── wsgi.py                  # WSGI 配置
└── user/                        # 用户应用
    ├── models.py                # 数据模型
    ├── views.py                 # 视图函数
    ├── serializers.py           # 序列化器
    ├── urls.py                  # 用户路由
    └── utils.py                 # 工具函数
```

## 环境配置

### 启动后端服务

```bash
cd backend
python manage.py runserver
```

服务默认运行在: `http://localhost:8000`

### 数据库迁移

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

### 用户相关接口

#### 1. 用户注册

**接口地址**: `POST /user/register/`

**请求参数**:
```json
{
    "userName": "string",    // 用户名，必填，最大长度20字符，唯一
    "password": "string"     // 密码，必填
}
```

**成功响应** (201):
```json
{
    "message": "注册成功",
    "user_id": "1",
    "userName": "testuser",
    "session_key": "session_key_string"
}
```

**说明**: 
- 注册成功后会自动登录，设置Session Cookie
- 无需再次调用登录接口

**失败响应** (400):
```json
{
    "error": "用户名已存在"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/user/register/ \
  -H "Content-Type: application/json" \
  -d '{"userName": "testuser", "password": "password123"}'
```

#### 2. 用户登录

**接口地址**: `POST /user/login/`

**请求参数**:
```json
{
    "userName": "string",    // 用户名，必填
    "password": "string"     // 密码，必填
}
```

**成功响应** (200):
```json
{
    "message": "登录成功",
    "user_id": "1",
    "userName": "testuser",
    "session_key": "session_key_string"
}
```

**说明**: 
- 登录成功后，服务器会自动设置Session Cookie
- 前端无需手动处理Cookie，浏览器会自动保存和发送
- Session有效期为7天

**失败响应** (400):
```json
{
    "non_field_errors": ["用户名或密码错误"]
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/user/login/ \
  -H "Content-Type: application/json" \
  -d '{"userName": "testuser", "password": "password123"}'
```

#### 3. 用户注销

**接口地址**: `POST /user/logout/`

**请求参数**: 无需参数

**成功响应** (200):
```json
{
    "message": "注销成功",
    "detail": "会话已清除，用户已注销"
}
```

**说明**: 
- 注销后会清除服务器端Session数据
- 浏览器Cookie也会失效

**说明**: 
- 由于系统采用无状态API设计，注销接口主要用于前端清理本地存储的用户信息
- 无需传递任何参数，调用即表示注销成功

**示例请求**:
```bash
curl -X POST http://localhost:8000/user/logout/ \
  -H "Content-Type: application/json" \
  --cookie-jar cookies.txt --cookie cookies.txt
```

#### 4. 检查登录状态

**接口地址**: `GET /user/check-login/`

**请求参数**: 无需参数，通过Cookie中的Session信息判断

**成功响应** (200) - 已登录:
```json
{
    "is_logged_in": true,
    "user_id": "1",
    "userName": "testuser",
    "login_time": "2025-07-27T10:30:00.000Z",
    "session_key": "session_key_string"
}
```

**成功响应** (200) - 未登录:
```json
{
    "is_logged_in": false,
    "message": "用户未登录"
}
```

**说明**: 
- 用于前端页面检测用户登录状态
- 根据Cookie中的Session信息自动判断
- 可在页面加载时调用，实现自动登录检测

**示例请求**:
```bash
curl -X GET http://localhost:8000/user/check-login/ \
  --cookie cookies.txt
```

### 睡眠记录相关接口

#### 5. 获取睡眠记录列表

**接口地址**: `GET /user/sleep-records/`

**请求参数** (查询参数):
- `days`: 获取最近几天的记录，默认30天
- `page`: 页码，默认1
- `page_size`: 每页记录数，默认10

**成功响应** (200):
```json
{
    "count": 25,
    "total_pages": 3,
    "current_page": 1,
    "has_next": true,
    "has_previous": false,
    "results": [
        {
            "id": 1,
            "user": 1,
            "user_name": "testuser",
            "date": "2025-07-27",
            "sleep_time": "23:30:00",
            "wake_time": "07:00:00",
            "sleep_duration": "07:30:00",
            "sleep_duration_hours": 7.5,
            "created_at": "2025-07-27T15:30:00.000Z",
            "updated_at": "2025-07-27T15:30:00.000Z"
        }
    ]
}
```

**示例请求**:
```bash
curl -X GET "http://localhost:8000/user/sleep-records/?days=7&page=1" \
  --cookie cookies.txt
```

#### 6. 创建睡眠记录

**接口地址**: `POST /user/sleep-records/create/`

**请求参数**:
```json
{
    "date": "2025-07-27",           // 日期，格式：YYYY-MM-DD
    "sleep_time": "23:30:00",       // 入睡时间，格式：HH:MM:SS
    "wake_time": "07:00:00"         // 起床时间，格式：HH:MM:SS
}
```

**成功响应** (201):
```json
{
    "message": "睡眠记录创建成功",
    "data": {
        "id": 1,
        "user": 1,
        "user_name": "testuser",
        "date": "2025-07-27",
        "sleep_time": "23:30:00",
        "wake_time": "07:00:00",
        "sleep_duration": "07:30:00",
        "sleep_duration_hours": 7.5,
        "created_at": "2025-07-27T15:30:00.000Z",
        "updated_at": "2025-07-27T15:30:00.000Z"
    }
}
```

**失败响应** (400):
```json
{
    "error": "日期 2025-07-27 的睡眠记录已存在，请使用更新接口"
}
```

**示例请求**:
```bash
curl -X POST http://localhost:8000/user/sleep-records/create/ \
  -H "Content-Type: application/json" \
  --cookie cookies.txt \
  -d '{"date": "2025-07-27", "sleep_time": "23:30:00", "wake_time": "07:00:00"}'
```

#### 7. 获取睡眠记录详情

**接口地址**: `GET /user/sleep-records/{record_id}/`

**成功响应** (200):
```json
{
    "id": 1,
    "user": 1,
    "user_name": "testuser",
    "date": "2025-07-27",
    "sleep_time": "23:30:00",
    "wake_time": "07:00:00",
    "sleep_duration": "07:30:00",
    "sleep_duration_hours": 7.5,
    "created_at": "2025-07-27T15:30:00.000Z",
    "updated_at": "2025-07-27T15:30:00.000Z"
}
```

#### 8. 更新睡眠记录

**接口地址**: `PUT /user/sleep-records/{record_id}/`

**请求参数**: 同创建接口，支持部分更新

**成功响应** (200):
```json
{
    "message": "睡眠记录更新成功",
    "data": { /* 更新后的记录数据 */ }
}
```

#### 9. 删除睡眠记录

**接口地址**: `DELETE /user/sleep-records/{record_id}/`

**成功响应** (200):
```json
{
    "message": "睡眠记录删除成功"
}
```

#### 10. 获取睡眠统计

**接口地址**: `GET /user/sleep-statistics/`

**请求参数** (查询参数):
- `days`: 统计最近几天的数据，默认7天

**成功响应** (200):
```json
{
    "statistics": {
        "total_records": 7,
        "average_sleep_hours": 7.8,
        "total_sleep_hours": 54.6,
        "longest_sleep": {
            "date": "2025-07-25",
            "hours": 8.5
        },
        "shortest_sleep": {
            "date": "2025-07-23",
            "hours": 6.5
        },
        "date_range": {
            "start_date": "2025-07-21",
            "end_date": "2025-07-27",
            "days": 7
        }
    }
}
```

**示例请求**:
```bash
curl -X GET "http://localhost:8000/user/sleep-statistics/?days=30" \
  --cookie cookies.txt
```

## 数据模型

### User (用户模型)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 用户ID | 主键，自动递增 |
| userName | CharField | 用户名 | 最大长度20，唯一 |
| password | CharField | 密码 | 最大长度64，加密存储 |

### SleepRecord (睡眠记录模型)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 记录ID | 主键，自动递增 |
| user | ForeignKey | 用户 | 外键，关联User模型 |
| date | DateField | 日期 | 记录日期，与用户联合唯一 |
| sleep_time | TimeField | 入睡时间 | 格式：HH:MM:SS |
| wake_time | TimeField | 起床时间 | 格式：HH:MM:SS |
| sleep_duration | DurationField | 睡眠时长 | 自动计算，只读 |
| created_at | DateTimeField | 创建时间 | 自动添加 |
| updated_at | DateTimeField | 更新时间 | 自动更新 |

**说明**:
- 每个用户每天只能有一条睡眠记录
- 睡眠时长会根据入睡时间和起床时间自动计算
- 如果起床时间早于入睡时间，系统会认为是第二天起床
- 提供 `sleep_duration_hours` 属性返回以小时为单位的睡眠时长

## 前端对接说明

### 1. 跨域和Cookie配置

后端已配置允许 `http://localhost:5173` 的跨域请求，并支持Cookie传递。

**重要**: 前端请求时必须设置 `credentials: 'include'` 以支持Cookie：

```javascript
// Axios 全局配置
axios.defaults.withCredentials = true;

// 或在单个请求中设置
axios.post('http://localhost:8000/user/login/', data, {
    withCredentials: true
});

// Fetch API
fetch('http://localhost:8000/user/login/', {
    method: 'POST',
    credentials: 'include',  // 重要：包含Cookie
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

### 2. Session认证机制

- 用户登录/注册成功后，服务器自动设置Session Cookie
- 后续请求浏览器会自动携带Cookie，无需手动处理
- Session有效期为7天，可通过 `/user/check-login/` 检查状态
- 注销后Session会被清除

### 3. 请求格式

- 所有 POST 请求需要设置 `Content-Type: application/json`
- 请求体使用 JSON 格式
- **重要**: 必须设置 `credentials: 'include'` 以支持Cookie

### 4. 错误处理

- 成功请求返回 2xx 状态码
- 客户端错误返回 4xx 状态码
- 服务器错误返回 5xx 状态码

### 5. 前端示例代码

#### JavaScript/Axios 示例

```javascript
// 配置 axios 支持 cookie
axios.defaults.withCredentials = true;

// 用户注册
async function register(userName, password) {
    try {
        const response = await axios.post('http://localhost:8000/user/register/', {
            userName,
            password
        });
        console.log('注册成功，已自动登录:', response.data);
        return response.data;
    } catch (error) {
        console.error('注册失败:', error.response.data);
        throw error;
    }
}

// 用户登录
async function login(userName, password) {
    try {
        const response = await axios.post('http://localhost:8000/user/login/', {
            userName,
            password
        });
        console.log('登录成功:', response.data);
        return response.data;
    } catch (error) {
        console.error('登录失败:', error.response.data);
        throw error;
    }
}

// 用户注销
async function logout() {
    try {
        const response = await axios.post('http://localhost:8000/user/logout/');
        console.log('注销成功:', response.data);
        return response.data;
    } catch (error) {
        console.error('注销失败:', error.response.data);
        throw error;
    }
}

// 检查登录状态
async function checkLogin() {
    try {
        const response = await axios.get('http://localhost:8000/user/check-login/');
        return response.data;
    } catch (error) {
        console.error('检查登录状态失败:', error.response.data);
        throw error;
    }
}

// 获取睡眠记录列表
async function getSleepRecords(days = 30, page = 1, pageSize = 10) {
    try {
        const response = await axios.get(`http://localhost:8000/user/sleep-records/?days=${days}&page=${page}&page_size=${pageSize}`);
        return response.data;
    } catch (error) {
        console.error('获取睡眠记录失败:', error.response.data);
        throw error;
    }
}

// 创建睡眠记录
async function createSleepRecord(date, sleepTime, wakeTime) {
    try {
        const response = await axios.post('http://localhost:8000/user/sleep-records/create/', {
            date,
            sleep_time: sleepTime,
            wake_time: wakeTime
        });
        console.log('睡眠记录创建成功:', response.data);
        return response.data;
    } catch (error) {
        console.error('创建睡眠记录失败:', error.response.data);
        throw error;
    }
}

// 更新睡眠记录
async function updateSleepRecord(recordId, data) {
    try {
        const response = await axios.put(`http://localhost:8000/user/sleep-records/${recordId}/`, data);
        console.log('睡眠记录更新成功:', response.data);
        return response.data;
    } catch (error) {
        console.error('更新睡眠记录失败:', error.response.data);
        throw error;
    }
}

// 删除睡眠记录
async function deleteSleepRecord(recordId) {
    try {
        const response = await axios.delete(`http://localhost:8000/user/sleep-records/${recordId}/`);
        console.log('睡眠记录删除成功:', response.data);
        return response.data;
    } catch (error) {
        console.error('删除睡眠记录失败:', error.response.data);
        throw error;
    }
}

// 获取睡眠统计
async function getSleepStatistics(days = 7) {
    try {
        const response = await axios.get(`http://localhost:8000/user/sleep-statistics/?days=${days}`);
        return response.data;
    } catch (error) {
        console.error('获取睡眠统计失败:', error.response.data);
        throw error;
    }
}
```

#### Vue.js 示例

```vue
<template>
  <div>
    <!-- 登录状态显示 -->
    <div v-if="isLoggedIn" class="user-info">
      <p>当前用户: {{ currentUser.userName }}</p>
      <button @click="handleLogout">注销</button>
    </div>
    
    <!-- 未登录时显示登录注册表单 -->
    <div v-else>
      <!-- 注册表单 -->
      <form @submit.prevent="handleRegister">
        <h3>用户注册</h3>
        <input v-model="registerForm.userName" placeholder="用户名" required />
        <input v-model="registerForm.password" type="password" placeholder="密码" required />
        <button type="submit">注册</button>
      </form>
      
      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin">
        <h3>用户登录</h3>
        <input v-model="loginForm.userName" placeholder="用户名" required />
        <input v-model="loginForm.password" type="password" placeholder="密码" required />
        <button type="submit">登录</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

// 配置 axios 支持 cookie
axios.defaults.withCredentials = true

export default {
  data() {
    return {
      registerForm: {
        userName: '',
        password: ''
      },
      loginForm: {
        userName: '',
        password: ''
      },
      currentUser: null,
      isLoggedIn: false
    }
  },
  methods: {
    async handleRegister() {
      try {
        const response = await axios.post('http://localhost:8000/user/register/', this.registerForm)
        alert('注册成功，已自动登录！')
        this.currentUser = response.data
        this.isLoggedIn = true
        // 清空表单
        this.registerForm = { userName: '', password: '' }
      } catch (error) {
        alert('注册失败：' + error.response.data.error)
      }
    },
    
    async handleLogin() {
      try {
        const response = await axios.post('http://localhost:8000/user/login/', this.loginForm)
        alert('登录成功！')
        this.currentUser = response.data
        this.isLoggedIn = true
        // 清空表单
        this.loginForm = { userName: '', password: '' }
      } catch (error) {
        alert('登录失败：用户名或密码错误')
      }
    },
    
    async handleLogout() {
      try {
        const response = await axios.post('http://localhost:8000/user/logout/')
        alert('注销成功！')
        this.currentUser = null
        this.isLoggedIn = false
      } catch (error) {
        alert('注销失败：' + error.response.data)
      }
    },
    
    async checkLoginStatus() {
      try {
        const response = await axios.get('http://localhost:8000/user/check-login/')
        if (response.data.is_logged_in) {
          this.currentUser = response.data
          this.isLoggedIn = true
        } else {
          this.currentUser = null
          this.isLoggedIn = false
        }
      } catch (error) {
        console.error('检查登录状态失败:', error)
        this.isLoggedIn = false
      }
    }
  },
  
  async mounted() {
    // 页面加载时自动检查登录状态
    await this.checkLoginStatus()
    if (savedUser) {
      this.currentUser = JSON.parse(savedUser)
      this.isLoggedIn = true
    }
  }
}
</script>
```

## 开发注意事项

### 1. 密码安全

- 密码使用 Django 内置 `make_password` 进行加密存储
- 验证时使用 `check_password` 进行安全比对

### 2. 字段命名

- 模型中使用 `userName` (驼峰命名)
- 请确保前后端字段名保持一致

### 3. 调试建议

- 使用浏览器开发者工具查看网络请求
- 检查请求头和响应状态码
- 查看 Django 服务器控制台输出

## 后续扩展

当前版本已实现的功能：

- [x] **用户认证系统**
  - [x] 用户注册和登录
  - [x] Session-Cookie认证
  - [x] 用户注销
  - [x] 登录状态检查

- [x] **睡眠记录管理**
  - [x] 睡眠记录的增删改查
  - [x] 自动计算睡眠时长
  - [x] 睡眠数据统计分析
  - [x] 分页和时间范围查询

- [x] **后台管理系统**
  - [x] 用户管理界面
  - [x] 睡眠记录查看

后续可以扩展的功能：

- [ ] JWT Token 认证
- [ ] 用户个人信息管理（年龄、性别、身高体重等）
- [ ] 其他健康数据记录（运动、饮食、心率等）
- [ ] 健康报告生成
- [ ] 数据可视化图表
- [ ] 健康提醒和建议
- [ ] 权限控制和角色管理
- [ ] 数据导出功能

## 联系信息

如有问题，请联系开发团队或查看项目文档。
