/**
 * 带Token支持的Vue认证服务
 */
class TokenAuthService {
    constructor() {
        this.baseURL = 'http://127.0.0.1:8000/api/user';
        this.csrfToken = null;
        this.authToken = null;
        this.isAuthenticated = false;
        this.currentUser = null;
    }

    /**
     * 获取CSRF token
     */
    async getCSRFToken() {
        try {
            const response = await fetch(`${this.baseURL}/csrf-token/`, {
                method: 'GET',
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.csrfToken = data.csrftoken;
                
                // 也尝试从cookie中获取
                const cookieToken = this.getCSRFTokenFromCookie();
                if (cookieToken) {
                    this.csrfToken = cookieToken;
                }
                
                return this.csrfToken;
            }
        } catch (error) {
            console.error('获取CSRF token失败:', error);
        }
        return null;
    }

    /**
     * 从cookie中获取CSRF token
     */
    getCSRFTokenFromCookie() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return null;
    }

    /**
     * 确保有CSRF token
     */
    async ensureCSRFToken() {
        if (!this.csrfToken) {
            await this.getCSRFToken();
        }
        return this.csrfToken;
    }

    /**
     * 发送API请求
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        // 默认选项
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        };

        // 合并选项
        const requestOptions = { ...defaultOptions, ...options };

        // 添加Authorization头部
        if (this.authToken) {
            requestOptions.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        // 如果是POST、PUT、DELETE等需要CSRF token的请求
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(requestOptions.method?.toUpperCase())) {
            await this.ensureCSRFToken();
            if (this.csrfToken) {
                requestOptions.headers['X-CSRFToken'] = this.csrfToken;
            }
        }

        try {
            const response = await fetch(url, requestOptions);
            
            // 检查是否需要重新获取CSRF token
            if (response.status === 403 && !this.csrfToken) {
                await this.getCSRFToken();
                if (this.csrfToken) {
                    requestOptions.headers['X-CSRFToken'] = this.csrfToken;
                    // 重试请求
                    return await fetch(url, requestOptions);
                }
            }

            return response;
        } catch (error) {
            console.error(`请求失败: ${error.message}`);
            throw error;
        }
    }

    /**
     * 登录
     */
    async login(userName, password) {
        try {
            const response = await this.request('/login/', {
                method: 'POST',
                body: JSON.stringify({
                    userName: userName,
                    password: password
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.isAuthenticated = true;
                this.authToken = data.auth_token;  // 保存认证token
                this.currentUser = {
                    id: data.user_id,
                    userName: data.userName
                };
                
                // 将token保存到localStorage以便页面刷新后恢复
                localStorage.setItem('auth_token', this.authToken);
                localStorage.setItem('user_info', JSON.stringify(this.currentUser));
                
                return { success: true, data: data };
            } else {
                return { success: false, error: data };
            }
        } catch (error) {
            console.error('登录请求失败:', error);
            return { success: false, error: { message: '网络错误，请检查网络连接' } };
        }
    }

    /**
     * 登出
     */
    async logout() {
        try {
            // 先清除本地状态
            this.isAuthenticated = false;
            this.currentUser = null;
            const tokenToRevoke = this.authToken;
            this.authToken = null;
            
            // 清除本地存储
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_info');
            
            return { success: true, data: { message: "登出成功" } };
        } catch (error) {
            console.error('登出过程中发生错误:', error);
            // 即使出错也要清除本地状态
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_info');
            return { success: false, error: { message: '网络错误' } };
        }
    }

    /**
     * 检查登录状态
     */
    async checkLoginStatus() {
        try {
            // 首先尝试从localStorage恢复token
            const savedToken = localStorage.getItem('auth_token');
            const savedUserInfo = localStorage.getItem('user_info');
            
            if (savedToken) {
                this.authToken = savedToken;
                if (savedUserInfo) {
                    this.currentUser = JSON.parse(savedUserInfo);
                }
            }
            
            // 发送请求验证token
            const response = await this.request('/check-login/', {
                method: 'GET'
            });

            const data = await response.json();
            
            if (response.ok && data.is_authenticated) {
                this.isAuthenticated = true;
                this.currentUser = {
                    id: data.user_id,
                    userName: data.user_name
                };
                // 更新token（可能有刷新）
                if (data.auth_token) {
                    this.authToken = data.auth_token;
                    localStorage.setItem('auth_token', this.authToken);
                }
                return { success: true, data: data };
            } else {
                this.isAuthenticated = false;
                this.currentUser = null;
                this.authToken = null;
                // 清除本地存储
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_info');
                return { success: false, data: data };
            }
        } catch (error) {
            console.error('检查登录状态失败:', error);
            this.isAuthenticated = false;
            this.currentUser = null;
            this.authToken = null;
            // 清除本地存储
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_info');
            return { success: false, error: { message: '网络错误' } };
        }
    }

    /**
     * 获取用户信息
     */
    async getUserProfile() {
        try {
            const response = await this.request('/profile/', {
                method: 'GET'
            });

            const data = await response.json();
            return response.ok ? { success: true, data } : { success: false, error: data };
        } catch (error) {
            return { success: false, error: { message: '网络错误' } };
        }
    }

    /**
     * 注册
     */
    async register(userName, password) {
        try {
            const response = await this.request('/register/', {
                method: 'POST',
                body: JSON.stringify({
                    userName: userName,
                    password: password
                })
            });

            const data = await response.json();
            return response.ok ? { success: true, data } : { success: false, error: data };
        } catch (error) {
            return { success: false, error: { message: '网络错误' } };
        }
    }

    /**
     * 获取当前的认证token
     */
    getToken() {
        return this.authToken;
    }

    /**
     * 设置认证token
     */
    setToken(token) {
        this.authToken = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    /**
     * 检查是否已认证
     */
    isLoggedIn() {
        return this.isAuthenticated && this.authToken;
    }

    /**
     * 获取用户信息
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * 调试session信息
     */
    async debugSession() {
        try {
            const response = await this.request('/debug-session/', {
                method: 'GET'
            });

            const data = await response.json();
            return response.ok ? { success: true, data } : { success: false, error: data };
        } catch (error) {
            return { success: false, error: { message: '网络错误' } };
        }
    }

    /**
     * 初始化 - 获取CSRF token并检查登录状态
     */
    async initialize() {
        try {
            // 获取CSRF token
            await this.getCSRFToken();
            
            // 检查登录状态
            await this.checkLoginStatus();
            
            return true;
        } catch (error) {
            console.error('初始化认证服务失败:', error);
            return false;
        }
    }
}

// 创建单例实例
const tokenAuthService = new TokenAuthService();

export default tokenAuthService;
