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
    "message": "注册成功"
}
```

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
    "userName": "testuser"
}
```

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

## 数据模型

### User (用户模型)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | Integer | 用户ID | 主键，自动递增 |
| userName | CharField | 用户名 | 最大长度20，唯一 |
| password | CharField | 密码 | 最大长度64，加密存储 |

## 前端对接说明

### 1. 跨域配置

后端已配置允许 `http://localhost:5173` 的跨域请求，适配 Vite 开发服务器。

### 2. 请求格式

- 所有 POST 请求需要设置 `Content-Type: application/json`
- 请求体使用 JSON 格式

### 3. 错误处理

- 成功请求返回 2xx 状态码
- 客户端错误返回 4xx 状态码
- 服务器错误返回 5xx 状态码

### 4. 前端示例代码

#### JavaScript/Axios 示例

```javascript
// 用户注册
async function register(userName, password) {
    try {
        const response = await axios.post('http://localhost:8000/user/register/', {
            userName,
            password
        });
        console.log('注册成功:', response.data);
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
```

#### Vue.js 示例

```vue
<template>
  <div>
    <!-- 注册表单 -->
    <form @submit.prevent="handleRegister">
      <input v-model="registerForm.userName" placeholder="用户名" required />
      <input v-model="registerForm.password" type="password" placeholder="密码" required />
      <button type="submit">注册</button>
    </form>
    
    <!-- 登录表单 -->
    <form @submit.prevent="handleLogin">
      <input v-model="loginForm.userName" placeholder="用户名" required />
      <input v-model="loginForm.password" type="password" placeholder="密码" required />
      <button type="submit">登录</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

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
      }
    }
  },
  methods: {
    async handleRegister() {
      try {
        const response = await axios.post('http://localhost:8000/user/register/', this.registerForm)
        alert('注册成功！')
      } catch (error) {
        alert('注册失败：' + error.response.data.error)
      }
    },
    
    async handleLogin() {
      try {
        const response = await axios.post('http://localhost:8000/user/login/', this.loginForm)
        alert('登录成功！')
        // 保存用户信息到本地存储
        localStorage.setItem('user', JSON.stringify(response.data))
      } catch (error) {
        alert('登录失败：用户名或密码错误')
      }
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

当前版本仅实现基础的用户注册和登录功能，后续可以扩展：

- [ ] JWT Token 认证
- [ ] 用户信息管理
- [ ] 健康数据记录
- [ ] 权限控制
- [ ] 数据统计分析

## 联系信息

如有问题，请联系开发团队或查看项目文档。
