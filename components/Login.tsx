import React, { useState } from 'react';
import { Compass, ShieldCheck, Loader2, Mail, Lock, UserPlus, LogIn } from 'lucide-react';

// 市场标准的微信官方图标
const WeChatIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M8.5,14.5c4.7,0,8.5-3.4,8.5-7.5c0-4.1-3.8-7.5-8.5-7.5c-4.7,0-8.5,3.4-8.5,7.5c0,4.1,3.8,7.5,8.5,7.5 c0.5,0,1-0.1,1.5-0.2c0.4,0,0.8,0.1,1.1,0.3c0.7,0.4,1.9,1,2.5,1.2c0.3,0.1,0.5-0.2,0.3-0.5c-0.2-0.5-0.6-1.3-0.8-1.8 c-0.1-0.2,0-0.4,0.1-0.6C12.4,13.6,10.5,14.5,8.5,14.5z M17.5,15c-0.3,0-0.6,0-1,0c-0.2,0-0.3,0-0.4,0.2c-1.3,1.3-3.1,2.1-5.1,2.1 c-0.2,0-0.5,0-0.7,0c-0.2,0-0.3,0.1-0.3,0.3c0,4,4,7.2,9,7.2c2,0,3.8-0.8,5.3-2.1c0.1-0.1,0.3-0.1,0.5,0c0.3,0.1,1.3,0.7,2.2,0.9 c0.3,0.1,0.5-0.2,0.3-0.5c-0.2-0.5-0.8-1.6-1-2.2c-0.1-0.2-0.1-0.4,0.1-0.5C27,19.3,27.5,17.9,27.5,16.4 C27.5,12.2,23,9.7,17.5,15z" transform="scale(0.8) translate(1,1)" />
    {/* 使用更简单的 SVG Path 来确保兼容性，下面是标准重绘版 */}
    <path d="M16.5 10C16.5 7.51 13.5 5.5 10 5.5C6.5 5.5 3.5 7.51 3.5 10C3.5 12.49 6.5 14.5 10 14.5C10.55 14.5 11.08 14.44 11.59 14.33C11.75 14.3 11.97 14.36 12.11 14.48C12.63 14.92 13.78 15.65 14.82 15.82C15.02 15.85 15.15 15.65 15.05 15.48C14.86 15.15 14.41 14.35 14.28 13.9C14.22 13.73 14.27 13.55 14.38 13.43C15.68 12.56 16.5 11.35 16.5 10Z" />
    <path d="M21.5 16C21.5 13.79 19.3 11.8 16.8 11.8C16.66 11.8 16.52 11.8 16.39 11.81C16.46 12.19 16.5 12.59 16.5 13C16.5 15.69 14.48 18.06 11.41 18.66C12.16 19.5 13.5 20.2 15.5 20.2C16.03 20.2 16.54 20.14 17.03 20.03C17.18 20 17.4 20.06 17.53 20.17C18.04 20.61 19.16 21.32 20.18 21.48C20.37 21.51 20.5 21.31 20.4 21.15C20.22 20.83 19.78 20.04 19.65 19.61C19.59 19.44 19.64 19.27 19.75 19.15C20.85 18.36 21.5 17.26 21.5 16Z" />
  </svg>
);

// 市场标准的苹果官方实心图标
const AppleIcon = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.71 19.5C17.88 20.74 17 21.95 15.66 21.97C14.32 22 13.89 21.18 12.37 21.18C10.84 21.18 10.37 21.95 9.1 22C7.79 22.05 6.8 20.68 5.96 19.47C4.25 17 2.94 13 4.7 10.37C5.58 9.05 7.13 8.22 8.55 8.19C9.88 8.17 10.83 9.09 11.66 9.09C12.47 9.09 13.75 8.02 15.27 8.16C15.89 8.19 17.65 8.41 18.77 10.05C18.68 10.11 16.73 11.23 16.76 13.82C16.79 16.92 19.46 17.97 19.5 18C19.46 18.06 19.16 19.03 18.71 19.5ZM13 6.91C13.62 6.16 14.04 5.12 13.92 4.09C13 4.14 11.9 4.7 11.23 5.5C10.66 6.15 10.15 7.23 10.28 8.24C11.3 8.35 12.38 7.66 13 6.91Z" />
  </svg>
);

interface LoginProps {
  onLogin: () => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false); // 切换登录/注册
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    setIsLoading(true);
    setErrorMsg('');

    const endpoint = isSignUp ? '/auth/signup' : '/auth/login';

    try {
      const response = await fetch(`http://localhost:8001${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || '操作失败');
      }

      // 如果是注册，提示用户登录或直接登录
      if (isSignUp) {
        // 注册成功后自动切回登录，或者直接登录（视后端返回而定）
        setIsSignUp(false);
        setErrorMsg('注册成功！请直接点击登录。');
      } else {
        // 登录成功，保存 Token
        if (data.token) {
          localStorage.setItem('access_token', data.token);
          // 如果后端返回了 user 信息，也可以存储
          if (data.user) {
            localStorage.setItem('user_info', JSON.stringify(data.user));
          }
        }
        onLogin();
      }
    } catch (err: any) {
      console.error("Login/Signup error:", err);
      if (err.message && err.message.includes('Failed to fetch')) {
        setErrorMsg('无法连接服务器，请确认后端已启动 (backend/main.py)');
      } else {
        setErrorMsg(err.message || '网络连接错误');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (platform: string) => {
    // 暂时仅做演示
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      alert('第三方登录暂未连接后端');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-8 relative overflow-hidden">
      {/* 采用生命绿背景扩散光效 */}
      <div className="absolute top-[-20%] right-[-10%] w-full h-[70%] bg-gradient-to-b from-teal-100/40 to-transparent rounded-full blur-[140px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-80 h-80 bg-emerald-100/20 rounded-full blur-[100px] pointer-events-none"></div>

      <div className="w-full max-w-sm space-y-8 relative z-10">
        {/* 品牌标识 */}
        <div className="text-center space-y-6">
          <div className="relative inline-flex items-center justify-center">
            {/* 能量波动环 */}
            <div className="absolute inset-0 bg-teal-500/10 rounded-[40px] animate-pulse duration-[3000ms]"></div>

            <div className="relative w-24 h-24 bg-gradient-to-br from-teal-600 to-emerald-700 rounded-[36px] shadow-2xl shadow-teal-100 flex items-center justify-center">
              <Compass className="text-white w-12 h-12 stroke-[2.5]" />
            </div>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-black text-slate-800 tracking-tight">护肾罗盘</h1>
            <p className="text-teal-700/60 text-sm font-bold tracking-[0.1em] uppercase">Kidney Compass Intelligence</p>
          </div>
        </div>

        {/* 错误提示 */}
        {errorMsg && (
          <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-xl text-center border border-red-100">
            {errorMsg}
          </div>
        )}

        {/* 邮箱密码表单 */}
        <form onSubmit={handleAuth} className="space-y-4">
          <div className="bg-white p-1.5 rounded-[24px] border border-slate-200 shadow-sm flex items-center transition-all focus-within:ring-2 focus-within:ring-teal-500/20">
            <div className="pl-4 pr-2 text-slate-400">
              <Mail className="w-5 h-5" />
            </div>
            <input
              type="email"
              placeholder="请输入邮箱"
              className="flex-1 p-4 bg-transparent outline-none text-slate-800 font-bold placeholder:text-slate-300 placeholder:font-medium"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="bg-white p-1.5 rounded-[24px] border border-slate-200 shadow-sm flex items-center transition-all focus-within:ring-2 focus-within:ring-teal-500/20">
            <div className="pl-4 pr-2 text-slate-400">
              <Lock className="w-5 h-5" />
            </div>
            <input
              type="password"
              placeholder="请输入密码"
              className="flex-1 p-4 bg-transparent outline-none text-slate-800 font-bold placeholder:text-slate-300 placeholder:font-medium"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !email || !password}
            className="w-full py-5 bg-teal-600 text-white rounded-[24px] font-bold shadow-xl shadow-teal-100 flex items-center justify-center space-x-2 active:scale-95 hover:bg-teal-700 transition-all disabled:opacity-50"
          >
            {isLoading ? (
              <Loader2 className="w-6 h-6 animate-spin" />
            ) : isSignUp ? (
              <>
                <UserPlus className="w-5 h-5" />
                <span>注册新账号</span>
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                <span>进入罗盘</span>
              </>
            )}
          </button>
        </form>

        {/* 切换登录/注册状态 */}
        <div className="text-center">
          <button
            onClick={() => { setIsSignUp(!isSignUp); setErrorMsg(''); }}
            className="text-xs font-bold text-teal-600 hover:text-teal-700 transition-colors"
          >
            {isSignUp ? "已有账号？直接登录" : "没有账号？点击注册"}
          </button>
        </div>

        {/* 第三方登录方式 */}
        <div className="pt-4">
          <div className="flex items-center space-x-4 mb-8">
            <div className="h-px flex-1 bg-slate-200"></div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest px-2">快捷认证</span>
            <div className="h-px flex-1 bg-slate-200"></div>
          </div>

          <div className="grid grid-cols-2 gap-5 px-8">
            <button
              onClick={() => handleSocialLogin('wechat')}
              className="flex flex-col items-center space-y-3 group"
            >
              <div className="w-16 h-16 flex items-center justify-center bg-white rounded-[24px] border border-slate-100 shadow-sm text-slate-300 group-hover:text-[#07C160] group-hover:border-[#07C160]/20 group-hover:bg-[#07C160]/5 transition-all active:scale-90">
                <WeChatIcon className="w-9 h-9" />
              </div>
              <span className="text-[11px] text-slate-500 font-bold">微信</span>
            </button>

            <button
              onClick={() => handleSocialLogin('apple')}
              className="flex flex-col items-center space-y-3 group"
            >
              <div className="w-16 h-16 flex items-center justify-center bg-white rounded-[24px] border border-slate-100 shadow-sm text-slate-300 group-hover:text-black group-hover:border-slate-300 group-hover:bg-slate-50 transition-all active:scale-90">
                <AppleIcon className="w-8 h-8" />
              </div>
              <span className="text-[11px] text-slate-500 font-bold">Apple ID</span>
            </button>
          </div>
        </div>
      </div>

      {/* 底部合规声明 */}
      <div className="absolute bottom-10 flex flex-col items-center space-y-3">
        <div className="flex items-center space-x-2 px-3 py-1 bg-white rounded-full border border-slate-100 shadow-sm">
          <ShieldCheck className="w-3 h-3 text-teal-600" />
          <span className="text-[9px] font-bold text-slate-500 tracking-wider">数据遵循医疗级安全加密标准</span>
        </div>
      </div>
    </div>
  );
};

export default Login;