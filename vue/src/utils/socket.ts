import { io } from 'socket.io-client';

export class SocketService {
  private socket;
  // 使用 Map 保存事件名称到回调映射（原始回调 -> 包装后的回调）
  private listeners: Map<string, Map<Function, Function>> = new Map();

  constructor() {
    this.socket = io('http://localhost:5000', {
      transports: ['websocket', 'polling'], // 先尝试WebSocket，失败后回退到polling
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    });
    
    this.socket.on('connect', () => {
      console.log('Socket连接成功，ID:', this.socket.id);
    });
    
    this.socket.on('connect_error', (err) => {
      console.error('Socket连接错误:', err);
    });
    
    this.socket.on('disconnect', (reason) => {
      console.log('Socket断开连接，原因:', reason);
    });
  }

  on(event: string, callback: Function) {
    // 如果该事件尚未有绑定记录，先初始化一个 Map
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Map());
    }
    const eventListeners = this.listeners.get(event)!;
    // 如果回调已经绑定，则直接返回，不重复绑定
    if (eventListeners.has(callback)) {
      return;
    }
    // 包装回调函数，处理不同数据格式
    const wrappedCallback = (data: any) => {
      console.log(`接收到${event}事件:`, data);
      // 检查数据格式，如果包含data属性则传入data.data，否则直接传入data
      if (data && typeof data === 'object' && 'data' in data) {
        callback(data.data);
      } else {
        callback(data);
      }
    };
    eventListeners.set(callback, wrappedCallback);
    this.socket.on(event, wrappedCallback);
    console.log(`已注册${event}事件监听器`);
  }

  // 提供 off 方法，用于解绑事件监听器
  off(event: string, callback: Function) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners && eventListeners.has(callback)) {
      const wrappedCallback = eventListeners.get(callback)!;
      this.socket.off(event, wrappedCallback);
      eventListeners.delete(callback);
      console.log(`已移除${event}事件监听器`);
    }
  }

  emit(event: string, data: any) {
    console.log(`发送${event}事件:`, data);
    this.socket.emit(event, data);
  }

  disconnect() {
    console.log('主动断开Socket连接');
    this.socket.disconnect();
    this.listeners.clear();
  }
}
